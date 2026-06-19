from typing import List, Optional, Dict, Iterable, Sequence
import aspose.pycore
import aspose.pydrawing
import aspose.slides
import aspose.slides.ai
import aspose.slides.animation
import aspose.slides.charts
import aspose.slides.dom.ole
import aspose.slides.effects
import aspose.slides.excel
import aspose.slides.export
import aspose.slides.export.xaml
import aspose.slides.importing
import aspose.slides.ink
import aspose.slides.lowcode
import aspose.slides.mathtext
import aspose.slides.slideshow
import aspose.slides.smartart
import aspose.slides.spreadsheet
import aspose.slides.theme
import aspose.slides.util
import aspose.slides.vba
import aspose.slides.warnings

class Collect:
    '''Represents a group of methods intended to collect model objects of different types from :py:class:`aspose.slides.Presentation`.'''
    @staticmethod
    def shapes(pres: Presentation) -> Iterable[Shape]:
        '''Collects all instances of :py:class:`aspose.slides.Shape` in the :py:class:`aspose.slides.Presentation`.
        :param pres: Presentation to collect shapes
        :returns: Collection of all shapes that contain in the presentation'''
        ...

    ...

class Compress:
    '''Represents a group of methods intended to compress :py:class:`aspose.slides.Presentation`.'''
    @staticmethod
    def remove_unused_master_slides(pres: Presentation) -> None:
        '''Makes compression of the :py:class:`aspose.slides.Presentation` by removing unused master slides.
        :param pres: The presentation instance'''
        ...

    @staticmethod
    def remove_unused_layout_slides(pres: Presentation) -> None:
        '''Makes compression of the :py:class:`aspose.slides.Presentation` by removing unused layout slides.
        :param pres: The presentation instance'''
        ...

    @staticmethod
    def compress_embedded_fonts(pres: Presentation) -> None:
        '''Makes compression of the :py:class:`aspose.slides.Presentation` by removing unused characters from embedded fonts.
        :param pres: The presentation instance'''
        ...

    ...

class Convert:
    '''Represents a group of methods intended to convert :py:class:`aspose.slides.Presentation`.'''
    @overload
    @staticmethod
    def to_pdf(pres_path: str, out_path: str) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to PDF.
        :param pres_path: Path of the input presentation
        :param out_path: Output path'''
        ...

    @overload
    @staticmethod
    def to_pdf(pres_path: str, out_path: str, options: aspose.slides.export.IPdfOptions) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to PDF.
        :param pres_path: Path of the input presentation
        :param out_path: Output path
        :param options: Output PDF options'''
        ...

    @overload
    @staticmethod
    def to_pdf(pres: Presentation, out_path: str) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to PDF.
        :param pres: Input presentation
        :param out_path: Output path'''
        ...

    @overload
    @staticmethod
    def to_pdf(pres: Presentation, out_path: str, options: aspose.slides.export.IPdfOptions) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to PDF.
        :param pres: Input presentation
        :param out_path: Output path
        :param options: Output PDF options'''
        ...

    @overload
    @staticmethod
    def to_svg(pres_path: str) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to SVG.
        :param pres_path: Path of the input presentation'''
        ...

    @overload
    @staticmethod
    def to_svg(pres: Presentation, options: aspose.slides.export.ISVGOptions) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` to SVG.
        :param pres: Input presentation
        :param options: SVG export options'''
        ...

    @overload
    @staticmethod
    def to_jpeg(pres: Presentation, output_file_name: str) -> None:
        '''Converts the input presentation to a set of JPEG format images.  
                    If the output file name is given as "myPath/myFilename.jpeg", 
                    the result will be saved as a set of "myPath/myFilename_N.jpeg" files, where N is a slide number.
        :param pres: The input presentation.
        :param output_file_name: The output file name.'''
        ...

    @overload
    @staticmethod
    def to_jpeg(pres: Presentation, output_file_name: str, image_size: aspose.pydrawing.Size) -> None:
        '''Converts the input presentation to a set of JPEG format images.  
                    If the output file name is given as "myPath/myFilename.jpeg", 
                    the result will be saved as a set of "myPath/myFilename_N.jpeg" files, where N is a slide number.
        :param pres: The input presentation
        :param output_file_name: The output file name.
        :param image_size: The size of each generated image.'''
        ...

    @overload
    @staticmethod
    def to_jpeg(pres: Presentation, output_file_name: str, scale: float, options: aspose.slides.export.IRenderingOptions) -> None:
        '''Converts the input presentation to a set of JPEG format images.  
                    If the output file name is given as "myPath/myFilename.jpeg", 
                    the result will be saved as a set of "myPath/myFilename_N.jpeg" files, where N is a slide number.
        :param pres: The input presentation.
        :param output_file_name: The output file name.
        :param scale: The scaling factor applied to the output images relative to the original slide size.
        :param options: The rendering options.'''
        ...

    @overload
    @staticmethod
    def to_png(pres: Presentation, output_file_name: str) -> None:
        '''Converts the input presentation to a set of PNG format images.  
                    If the output file name is given as "myPath/myFilename.png", 
                    the result will be saved as a set of "myPath/myFilename_N.png" files, where N is a slide number.
        :param pres: The input presentation.
        :param output_file_name: The output file name.'''
        ...

    @overload
    @staticmethod
    def to_png(pres: Presentation, output_file_name: str, image_size: aspose.pydrawing.Size) -> None:
        '''Converts the input presentation to a set of PNG format images.  
                    If the output file name is given as "myPath/myFilename.png", 
                    the result will be saved as a set of "myPath/myFilename_N.png" files, where N is a slide number.
        :param pres: The input presentation
        :param output_file_name: The output file name.
        :param image_size: The size of each generated image.'''
        ...

    @overload
    @staticmethod
    def to_png(pres: Presentation, output_file_name: str, scale: float, options: aspose.slides.export.IRenderingOptions) -> None:
        '''Converts the input presentation to a set of PNG format images.  
                    If the output file name is given as "myPath/myFilename.png", 
                    the result will be saved as a set of "myPath/myFilename_N.png" files, where N is a slide number.
        :param pres: The input presentation.
        :param output_file_name: The output file name.
        :param scale: The scaling factor applied to the output images relative to the original slide size.
        :param options: The rendering options.'''
        ...

    @overload
    @staticmethod
    def to_tiff(pres: Presentation, output_file_name: str) -> None:
        '''Converts the input presentation to a set of TIFF format images.  
                    If the output file name is given as "myPath/myFilename.tiff", 
                    the result will be saved as a set of "myPath/myFilename_N.tiff" files, where N is a slide number.
        :param pres: The input presentation.
        :param output_file_name: The output file name.'''
        ...

    @overload
    @staticmethod
    def to_tiff(pres: Presentation, output_file_name: str, options: aspose.slides.export.ITiffOptions, multipage: bool) -> None:
        '''Converts the input presentation to TIFF format with custom options.
                    If the output file name is given as "myPath/myFilename.tiff" and ``multipage`` is ``false``, 
                    the result will be saved as a set of "myPath/myFilename_N.tiff" files, where N is a slide number.
                    Otherwise, if ``multipage`` is ``true``, the result will be a multi-page "myPath/myFilename.tiff" document.
        :param pres: The input presentation.
        :param output_file_name: The output file name.
        :param options: The TIFF saving options.
        :param multipage: Specifies whether the generated TIFF document should be a multi-page.'''
        ...

    @staticmethod
    def auto_by_extension(pres_path: str, out_path: str) -> None:
        '''Converts :py:class:`aspose.slides.Presentation` using the passed output path extension to determine the required export format.
        :param pres_path: Path of the input presentation
        :param out_path: Output path'''
        ...

    ...

class ForEach:
    '''Represents a group of methods intended to iterate over different :py:class:`aspose.slides.Presentation` model objects.
                These methods can be useful if you need to iterate and change some Presentation' elements formatting or content,
                 e.g. change each portion formatting.'''
    ...

class Merger:
    '''Represents a group of methods for merging PowerPoint presentations of the same format into one file.'''
    @overload
    @staticmethod
    def process(input_file_names: List[str], output_file_name: str) -> None:
        '''Merges multiple PowerPoint presentations of the same format into a single presentation file.
        :param input_file_names: An array of the input presentation file names.
        :param output_file_name: The output file name of the resulting merged presentation file.'''
        ...

    @overload
    @staticmethod
    def process(input_file_names: List[str], output_file_name: str, options: aspose.slides.export.ISaveOptions) -> None:
        '''Merges multiple PowerPoint presentations of the same format into a single presentation file.
        :param input_file_names: An array of the input presentation file names.
        :param output_file_name: The output file name of the resulting merged presentation file.
        :param options: The additional options that define how the merged presentation is saved.'''
        ...

    @overload
    @staticmethod
    def process(input_file_names: List[str], output_stream: io.RawIOBase) -> None:
        '''Merges multiple PowerPoint presentations of the same format into a single presentation file.
        :param input_file_names: An array of the input presentation file names.
        :param output_stream: The output stream.'''
        ...

    @overload
    @staticmethod
    def process(input_file_names: List[str], output_stream: io.RawIOBase, options: aspose.slides.export.ISaveOptions) -> None:
        '''Merges multiple PowerPoint presentations of the same format into a single presentation file.
        :param input_file_names: An array of the input presentation file names.
        :param output_stream: The output stream.
        :param options: The additional options that define how the merged presentation is saved.'''
        ...

    ...

