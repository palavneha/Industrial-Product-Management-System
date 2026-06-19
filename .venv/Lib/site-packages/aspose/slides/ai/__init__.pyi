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

class IAIConversation:
    '''Represents a conversation instance. Unlike regular AI calls, conversations retain the entire context.'''
    ...

class IAIWebClient:
    '''AI Web client interface. This interface enables to substitute different AI language models.
                Classes that implement this interface are supposed to be used along with `SlidesAIAgent`.'''
    def create_conversation(self) -> IAIConversation:
        '''Creates a conversation instance. Unlike regular AI calls, conversations retain the entire context.
        :returns: An :py:class:`aspose.slides.ai.IAIConversation` instance.'''
        ...

    ...

class OpenAIWebClient:
    '''Build-in lightweight OpenAI web client'''
    def __init__(self, model: str, api_key: str, organization_id: str):
        '''Creates instance of OpenAI Web client.
        :param model: OpenAI language model. Possible values:
                      - gpt-4o
                      - gpt-4o-mini
                      - o1
                      - o1-mini
                      - o3
                      - o3-mini
        :param api_key: OpenAI API key
        :param organization_id: Organization ID (optional)'''
        ...

    def create_conversation(self) -> IAIConversation:
        '''Creates a conversation instance. Unlike regular AI calls, conversations retain the entire context.
        :returns: An :py:class:`aspose.slides.ai.IAIConversation` instance.'''
        ...

    ...

class SlidesAIAgent:
    '''Provides AI-powered features for processing presentations.'''
    def __init__(self, ai_client: IAIWebClient):
        '''SlidesAIAgent constructor'''
        ...

    @overload
    def generate_presentation(self, description: str, presentation_content_amount: PresentationContentAmountType) -> IPresentation:
        '''Generates a presentation instance from a text description. Provide a topic, ideas, quotes, or text snippets in the required language.
        :param description: The topic, ideas, quotes, or text snippets.
        :param presentation_content_amount: The amount of content in the resulting presentation.'''
        ...

    @overload
    def generate_presentation(self, description: str, presentation_content_amount: PresentationContentAmountType, presentation_template: IPresentation) -> IPresentation:
        '''Generates a presentation instance from a text description. Provide a topic, ideas, quotes, or text snippets in the required language.
        :param description: The topic, ideas, quotes, or text snippets.
        :param presentation_content_amount: The amount of content in the resulting presentation.
        :param presentation_template: A presentation to use as a template for layout and design, replacing the default template.'''
        ...

    def translate(self, presentation: IPresentation, language: str) -> None:
        '''Translates a presentation to the specified language using AI (synchronous version).
        :param presentation: Target presentation
        :param language: Target language'''
        ...

    ...

class SlidesAIAgentException:
    '''Represents Slides AI Agent related exceptions.'''
    def __init__(self, message: str):
        '''Constructor allowing a message to be added to this exception.
        :param message: message'''
        ...

    ...

class PresentationContentAmountType:
    '''Specifies the amount of content included in the generated presentation, influencing both the number of slides and the level of detail per slide.'''
    @classmethod
    @property
    def BRIEF(cls) -> PresentationContentAmountType:
        '''Short and basic content.'''
        ...

    @classmethod
    @property
    def MEDIUM(cls) -> PresentationContentAmountType:
        '''A moderate amount of content.'''
        ...

    @classmethod
    @property
    def DETAILED(cls) -> PresentationContentAmountType:
        '''The most detailed option with extensive text.'''
        ...

    ...

