import unittest
import os.path
from fairy_tale.fairy_tale import PDF
from fpdf import FPDF


class TestPDF(unittest.TestCase):
    
    def test_inheritance(self):
        self.assertTrue(issubclass(PDF, FPDF))
        
    def test_init(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(os.path.dirname(current_dir), "fairy_tale")
        pdf = PDF(fonts_dir, os.path.join(current_dir, "test.pdf"))
        self.assertIsNotNone(pdf)
        
    def test_save_fairy_tales(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(os.path.dirname(current_dir), "fairy_tale")
        pdf_path = os.path.join(current_dir, "test.pdf")
        pdf = PDF(fonts_dir, os.path.join(current_dir, pdf_path))
        pdf.save_fairy_tales([("test", "test")])
        self.assertTrue(os.path.exists(pdf_path))


if __name__ == '__main__':
    unittest.main()