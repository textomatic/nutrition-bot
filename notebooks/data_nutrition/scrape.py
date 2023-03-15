# import eutils
# from pubmedflow import LazyPubmed
# title_query = ['nutrition']
# API_KEY = '7b9c89a970ae955f44126d6a53a655b9f808'
# pb  = LazyPubmed(title_query,
#                  folder_name='./pdf',
#                  #api_key=API_KEY,
#                  max_documents=10,
#                  download_pdf=True,
#                  scihub=True)

from paperscraper.pubmed import get_and_dump_pubmed_papers
covid19 = ['COVID-19', 'SARS-CoV-2']
ai = ['Artificial intelligence', 'Deep learning', 'Machine learning']
mi = ['Medical imaging']
query = [covid19, ai, mi]
get_and_dump_pubmed_papers(keywords=query, output_filepath='covid19_ai_imaging.jsonl')

# nutrition = ["nutrition"]
# query = [nutrition]
# get_and_dump_pubmed_papers(keywords=query, output_filepath='nutrition.jsonl')

# from scihub import SciHub

# sh = SciHub()
# print(dir(SciHub))
# keywords = 'Nutrition'
# result = sh.search(keywords, limit=10)
# print(result)

# for index, paper in enumerate(result.get("papers", [])):
#     sh.download(paper["doi"], path=f"pdf/{keywords.replace(' ', '_')}_{index}.pdf")
