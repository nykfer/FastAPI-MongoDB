from firecrawl import JsonConfig, FirecrawlApp
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import os
import dotenv

dotenv.load_dotenv()

class Firecrawl:
    def __init__(self):
        API_KEY = os.getenv("FIRECRAWL-API-KEY")
        self.app = FirecrawlApp(api_key=API_KEY)

    class ExtractSchema(BaseModel):
        company_mission: str
        supports_sso: bool
        is_open_source: bool
        is_in_yc: bool
    
    class ScrapeParameters(BaseModel):
        only_main_content: Optional[bool] = Field(default=True, description="Only return the main content of the page excluding headers, navs, footers, etc")
        timeout: Optional[int] = Field(default=30000, description="Timeout in milliseconds for the request")
        includeTags: Optional[List[str]] = Field(default=[], description="Tags to include in the output")
        excludeTags: Optional[List[str]] = Field(default=[], description="Tags to exclude from the output")
        maxAge: Optional[int] = Field(default=0, description="Returns a cached version of the page if it is younger than this age in milliseconds. If a cached version of the page is older than this value, the page will be scraped. If you do not need extremely fresh data, enabling this can speed up your scrapes by 500%. Defaults to 0, which disables caching")
        parsePDF: Optional[bool] = Field(default=False, description="Controls how PDF files are processed during scraping. When true, the PDF content is extracted and converted to markdown format, with billing based on the number of pages (1 credit per page). When false, the PDF file is returned in base64 encoding with a flat rate of 1 credit total")

    json_config = JsonConfig(
        schema=ExtractSchema
    )

    def get_structured_output(self, url:str, **extra):
        try:
            validated_parameters = self.ScrapeParameters(**extra)
        except ValidationError as e:
            raise ValueError(f"Invalid parameters: {e}")
        
        final_parameters = validated_parameters.model_dump()
        try:
            llm_extraction_result  = self.app.scrape_url(url,
                                                         formats=["json"],
                                                        json_options=self.json_config,
                                                        **final_parameters)
            return llm_extraction_result.json
        except ValueError as e:
            print("Error while parsing data")
