#python -W ignore download_pdf.py

from multiprocessing import Pool
import pandas as pd
from scidownl import scihub_download

def foo(first_last):
	print("foo", first_last[0], first_last[1])
	df_all = pd.read_pickle("./new_df.pickle")

	df_down = df_all[first_last[0]:first_last[1]]
	tried = []
	curr = 1
	for doi in df_down['doi']:
		print("-------------------------curr:{curr}----------------------------".format(curr=curr))
		print("doi:", doi)
		paper = f"https://doi.org/{doi}"
		paper_type = "doi"
		out = f'./pdf_new/{doi.replace("/", "_")}.pdf'
		scihub_download(paper, paper_type=paper_type, out=out)
		if curr%10 == 0:
			tried.append(doi)
			pd.DataFrame(tried).to_excel(f"{first_last[0]}_{first_last[1]}.xlsx", index=False)
		curr += 1
		

def pool_handler():
	p=Pool(3)
	p.map(foo, [(0,1000), (1000,2000), (2000,3000)])

if __name__ == '__main__':
	pool_handler()