import os
import asyncio
from argparse import ArgumentParser
from openai import AsyncOpenAI, OpenAIError
from fpdf import FPDF, TitleStyle
from fpdf.outline import OutlineSection
from typing import Self
from openai.types.beta.threads import Run
from openai.types.beta.assistant import Assistant


class FairyTale(AsyncOpenAI):
    """
    A class that represents a fairy tale generator.
    
    Attributes
    ----------
    assistant : Assistant
        An instance of GPT Assistant whose purpose is to generate fairy tales.
        See: https://platform.openai.com/docs/assistants
    responses : list[tuple[str, str]
        A list of tuples containing the content and title of all the fairy tales.
    """
    def __init__(self, api_key: str = None, *args: str) -> None:
        """
        Parameters
        ----------
        api_key : str
            A key to OpenAI API. May be omitted if Env Var OPENAI_API_KEY is set.
            See: https://platform.openai.com/api-keys
        args : str
            The topics you want GPT to tell you fairy tales about.
        """
        super().__init__(api_key=api_key)
        self.topics = list(args)
        self.assistant = None
        self.responses = None
                  
    @property
    def topics(self) -> list[str]:
        """
        Topics getter and setter.
        
        Returns
        -------
        list[str]
            The topics you want GPT to tell you fairy tales about.
        
        Raises
        ------
        ValueError
            If no topics are provided.
        """
        return self._topics
    
    @topics.setter
    def topics(self, *args: str) -> None:
        if not args or not any(*args):
            raise ValueError("At least one topic is required.")
        self._topics = list(*args)
    
    async def create_assistant(self, name: str, description: str, model: str) -> Assistant:
        """
        Creates a new GPT Assistant.
        
        Parameters
        ----------
        name : str
            The name of the assistant.
        description : str
            The description of the assistant.
        model : str
            The ID of the model to use for this assistant.
        
        Returns
        -------
        Assistant
            An instance of GPT Assistant.
            See: https://platform.openai.com/docs/assistants
        """
        self.assistant = await self.beta.assistants.create(
            name=name,
            description=description,
            model=model
        )
        return self.assistant
        
    async def delete_assistant(self) -> None:
        """Deletes the GPT Assistant."""
        await self.beta.assistants.delete(assistant_id=self.assistant.id)
        self.assistant = None
        
    async def wait_for_response(self, thread_id: str) -> Run:
        """
        Waits for the assistant to respond.
        
        Parameters
        ----------
        thread_id : str
            The ID of the thread.
        
        Returns
        -------
        Run
            An instance of GPT Run.
            See: https://platform.openai.com/docs/api-reference/runs
        """
        run = await self.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        while run.status == "queued" or run.status == "in_progress":
            run = await self.beta.threads.runs.retrieve(
                thread_id=thread_id, 
                run_id=run.id,
            )
            await asyncio.sleep(0.5)
        return run
            
    async def add_message(self, thread_id, message: str) -> None:
        """
        Adds user's message to the thread.
        
        Parameters
        ----------
        thread_id : str
            The ID of the thread.
        message : str
            The message to add.
        """
        await self.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
    
    async def get_fairy_tale(self, first_prompt: str, second_prompt: str) -> tuple[str, str] | None:
        """
        Generates a fairy tale.
        
        Parameters
        ----------
        first_prompt : str
            The first prompt to use to get the content of the fairy tale.
        second_prompt : str
            The second prompt to use to get the title of the fairy tale.
        
        Returns
        -------
        tuple[str, str] | None
            A tuple containing the content and title of the fairy tale.
            If there was an error generating a fairy tale, then None is returned.
        """
        thread = await self.beta.threads.create()
        await self.add_message(thread.id, first_prompt)
        run1 = await self.wait_for_response(thread.id)
        await self.add_message(thread.id, second_prompt)
        run2 = await self.wait_for_response(thread.id)    
        messages = await self.beta.threads.messages.list(thread_id=thread.id, order="asc")
        await self.beta.threads.delete(thread_id=thread.id)
        if run1.status == "completed" and run2.status == "completed":
            return (message.content[0].text.value 
                    for message in messages.data 
                    if message.role == "assistant")
        return None
    
    async def write_fairy_tales(self, first_prompt: str, second_prompt: str) -> list[tuple[str, str]]:
        """
        Generates fairy tales.
        
        Parameters
        ----------
        first_prompt : str
            The first prompt to use.
        second_prompt : str
            The second prompt to use.
        
        Returns
        -------
        Iterable[tuple[str, str]]
            An list of tuples containing the content and title of the fairy tales.
        """
        self.responses = await asyncio.gather(*(
            self.get_fairy_tale(
                f"{first_prompt}{topic}.",
                second_prompt
            ) 
            for topic in self.topics
        ))
        self.responses = filter(lambda x: x is not None, self.responses)
        self.responses = list(map(tuple, self.responses))
        return self.responses


class PDF(FPDF):
    """
    A class that represents a PDF document.
    
    Attributes
    ----------
    path : str
        The path to the PDF file to save the fairy tales to.
    """
    def __init__(self, fonts_dir: str, output_path: str) -> None:
        """
        Parameters
        ----------
        fonts_path : str
            The path to the fonts directory.
        output_path : str
            The path to the PDF file to save the fairy tales to.
        """
        super().__init__()
        self.path = output_path
        self.set_title("Fairy tales")
        self.set_author("ChatGPT")
        self.set_margin(20)
        self.add_font("Roboto", "", os.path.join(fonts_dir, 'Roboto-Regular.ttf'))
        self.add_font("Roboto", "B", os.path.join(fonts_dir, 'Roboto-Bold.ttf'))
        self.set_section_title_styles(TitleStyle("Roboto", "B", 20))
    
    def title_page(self) -> None:
        """Creates a title page."""
        self.add_page()
        self.set_font("Roboto", "B", 42)
        self.write(text="Fairy tales by ChatGPT\n\n")
        self.insert_toc_placeholder(self.table_of_contents)
    
    def table_of_contents(self, pdf: Self, outline: list[OutlineSection]) -> None:
        """
        Creates a table of contents.
        
        Parameters
        ----------
        pdf : PDF
            An instance of PDF.
        outline : list[OutlineSection]
            A list of sections.
        """
        pdf.set_font("Roboto", "", size=16)
        for number, section in enumerate(outline):
            link = pdf.add_link(page=section.page_number)
            pdf.write(text=f"{number+1}. {section.name} (p. {section.page_number})\n", link=link)

    def subtitle(self, text: str) -> None:
        """
        Adds a subtitle to the document.
        
        Parameters
        ----------
        text : str
            The text of the subtitle.
        """
        self.start_section(text)
        self.write(text="\n")
        
    def content(self, text: str, is_last: bool=False) -> None:
        """
        Adds a content to the document.
        
        Parameters
        ----------
        text : str
            The text of the content.
        is_last : bool
            Whether this is the last content. If so, then a new page is not added.
        """
        self.set_font("Roboto", size=14)
        self.write(text=text)
        self.write(text="\n")
        if not is_last:
            self.add_page()
     
    def save_fairy_tales(self, responses: list[tuple[str, str]]) -> None:
        """
        Saves the fairy tales to a PDF file.
        
        Parameters
        ----------
        responses : list[tuple[str, str]]
            A list of tuples containing the content and title of the fairy tales.
        """
        self.title_page()
        for i, (content, title) in enumerate(responses):
            if isinstance(content, str) and isinstance(title, str):
                self.subtitle(title)
                self.content(content, i==len(responses)-1)
            else:
                raise ValueError("Invalid response.")
        self.output(self.path)


async def run() -> None:
    """Creates a fairy tale generator and saves the generated fairy tales to a PDF file."""
    parser = ArgumentParser(description="Tells you a fairy tale.")
    parser.add_argument("-topics",
                        required=False,
                        nargs="*", 
                        help="The topics you want GPT to tell you a fairy tales about.")
    parser.add_argument("-key",
                        required=not os.environ.get("OPENAI_API_KEY"),
                        help="A key to OpenAI API. May be omitted if Env Var OPENAI_API_KEY is set. \
                        See: https://platform.openai.com/api-keys")
    args = parser.parse_args()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_name = "Fairy tales.pdf"
    output_path = os.path.join(os.getcwd(), output_file_name)   

    name = "Fairy tale teller"
    model = "gpt-3.5-turbo-1106"
    description = "You are a writer of fairy tales for children. " \
        "You can write a short fairy tale on any topic given by the user. " \
        "When asked about a fairy tale, you always respond with only the content of the fairy tale. " \
        "When asked about the title, you always respond with only the title of the fairy tale you wrote. " \
        "Do not use quotation marks for the title."
    first_prompt = "Write a fairy tale on the topic: "
    second_prompt = "Give me the title of this fairy tale. Do not use quotation marks."

    try:
        while args.topics is None:
            args.topics = input("Enter topics separated by commas: ").split(", ")
        fairy_tale = FairyTale(args.key, *args.topics)   
    except EOFError:
        print("\nExiting...")
        return
    
    try:
        print("Starting ChatGPT Assistant...")
        await fairy_tale.create_assistant(
            name=name,
            description=description,
            model=model
        )
        
        print("Generating text...")
        await fairy_tale.write_fairy_tales(first_prompt, second_prompt)
        
        print("Saving PDF...")
        pdf = PDF(current_dir, output_path)
        pdf.save_fairy_tales(fairy_tale.responses)   
    except OpenAIError as e:
        print(e)
        return
    except asyncio.exceptions.CancelledError:
        return
    finally:
        if fairy_tale.assistant is not None:
            print("Stopping ChatGPT Assistant...")
            try:
                await fairy_tale.delete_assistant()
            except OpenAIError as e:
                print(e)
                return

    
def main() -> None:
    """Wraps run() in asyncio.run()."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        exit(0)

if __name__ == "__main__":
    main()
        