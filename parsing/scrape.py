from firecrawl import JsonConfig, FirecrawlApp
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict
import os
import dotenv
import requests
import types

urls = ["https://futurumcareers.com/articles",
        "https://www.science.org/content/page/subject-collections",  # Genetics & Molecular Biology                      # Neuroscience
    "https://www.science.org/journal/sciimmunol",               # Immunology

    # Physical Sciences
    "https://www.sciencedaily.com/news/matter_energy/physics/", # Physics
    "https://phys.org/chemistry-news/",                         # Chemistry
    "https://science.nasa.gov",                                 # Astronomy & Space Science
    "https://www.issibern.ch/scientific-opportunities/forums/", # Space Science Forums

    # Environmental & Earth Sciences
    "https://www.sciencedaily.com/news/earth_climate/climate/", # Climate & Environment
    "https://www.bgs.ac.uk/news/",                              # Geosciences

    # Multidisciplinary & Forums
    "https://www.scienceforums.net/",                           # General Science Forums
    "https://ncas.ac.uk/for-staff/research-forums/"]

dotenv.load_dotenv()

class Firecrawl:
    def __init__(self):
        API_KEY = os.getenv("FIRECRAWL-API-KEY")
        self.app = FirecrawlApp(api_key=API_KEY)

    class ExtractSchema(BaseModel):
        url: str = Field(..., description="There is the url of scraped page")
        text: str = Field(default="Some text", description="All scraped content from a page")
        # science_field: str  = Field(..., examples=["math", "biology", "history", "economy", "finance"], description="Science fields that can be related to the web-page")
        # terms: List[str] = Field(..., examples=["function", "stock market"], description="Science terms mentioned in the content")
        # people_mentioned: Optional[List[str]] = Field(..., description="People that are mentioned in the content")
    
    class ErrorResponse(BaseModel):
        url: str = Field(..., description="There is the url of scraped page")
        error: str = Field(..., description="Some error happened during screping process")
    
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
            json_response = llm_extraction_result.json
            if isinstance(json_response, types.FunctionType):
                error_response = {"url": url, "error":f"Return function type: {str(type(json_response))}"}
                error_model = self.ErrorResponse(url=error_response["url"], error = error_response["error"])
                return error_model.model_dump()
            else:
                return json_response
        except requests.exceptions.HTTPError as e:
            # Check if the error is a timeout
            if "Request Timeout" in str(e):
                print(f"Skipping URL due to timeout: {url}")
                error_response = {"error": "Timeout - skipped scraping", "url": url}
                error_model = self.ErrorResponse(url=error_response["url"], error = error_response["error"])
                return error_model.model_dump()
            else:
                print(f"HTTP error scraping {url}: {e}")
                error_response = {"error": f"HTTP error scraping: {e}", "url": url}
                error_model = self.ErrorResponse(url=error_response["url"], error = error_response["error"])
                return error_model.model_dump()

if __name__ == "__main__":
    app = Firecrawl()
    for url in urls:
        result = app.get_structured_output(url=url)
        print(type(result))
        print(result)