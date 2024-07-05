import arxiv
import time
from googletrans import Translator
import requests

import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext

import argparse
import pickle

EST = -5
def get_time(location=9):
    t = time.time() - (location * 3600) + (EST * 3600)
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, _, _, _ = time.localtime(t)
    return tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec

def get_arxiv_info(id: list, filter_category: str = "cs", filter_author: str = ""):
    client = arxiv.Client()
    search_by_id = arxiv.Search(id_list=id)
    results = client.results(search_by_id)

    papers = dict()
    for i, result in enumerate(results):
        categories = result.categories

        # primary_category가 원하는 카테고리가 아니라면
        if not str(result.primary_category).startswith(filter_category) and filter_category != "":
            continue

        # category가 분야를 필터링,
        if "." not in filter_category:
            for j, c in enumerate(categories):
                category = c.split(".")[0]
                if category == filter_category: break
            if category != filter_category and j == len(categories) - 1: continue
        # category가 분야 중에서도 특정된 분야를 필터링,
        elif filter_category not in categories and filter_category != "":
            continue

        authors = result.authors
        author_list = [str(author) for author in authors]
        if filter_author not in author_list and filter_author != "":
            continue
        
        paper_info = dict()
        paper_info["categories"] = categories
        paper_info["primary_category"] = result.primary_category
        paper_info["title"] = result.title
        paper_info["abstract"] = result.summary.replace("\n", " ")
        paper_info["url"] = result.pdf_url
        
        date = result.updated
        paper_info["date"] = f"{date.year}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}"
        
        # preprocessing
        authors_string = ', '.join(author_list)
        paper_info["authors"] = authors_string
        papers[id[i]] = paper_info
        
    return papers

def concat_papers(separated_papers):
    papers = dict()
    for paper in separated_papers:
        for key in paper.keys():
            papers[key] = paper[key]
    return papers

def get_papers(year, month, start_code, end_code, filter_category="cs.AI", filter_author=""):
    if start_code > end_code:
        raise ValueError("start_code should be smaller than end_code")

    iteration = (end_code - start_code + 1) // 500
    separated_papers = list()
    for i in range(iteration):
        s, e = start_code + (500 * i), start_code + 500 * (i + 1)
        id = [f"{year}{str(month).zfill(2)}." + str(j).zfill(5) + "v1" for j in range(s, e + 1)]
        separated_papers.append(get_arxiv_info(id, filter_category, filter_author))
    id = [f"{year}{str(month).zfill(2)}." + str(j).zfill(5) + "v1" for j in range(e + 1, end_code + 1)]
    separated_papers.append(get_arxiv_info(id, filter_category, filter_author))

    return concat_papers(separated_papers)

def download_pdf(pdf_url, save_path):
    response = requests.get(pdf_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    # Google translator
    translator = Translator()
    tgt_lang_code = "ko"
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = get_time()

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", "-y", type=int, default=tm_year - 2000)
    parser.add_argument("--month", "-m", type=int, default=tm_mon)
    parser.add_argument("--start_code", "-s", type=int, default=0)
    parser.add_argument("--end_code", "-e", type=int, default=0)
    parser.add_argument("--filter_category", "-fc", type=str, default="cs")
    parser.add_argument("--filter_author", "-fa", type=str, default="")
    parser.add_argument("--data_path", "-p", type=str, default="")
    args = parser.parse_args()

    # Get Paper Information
    print("Getting papers... It may take a few minutes.")
    if args.data_path != "":
        with open(args.data_path, "rb") as f:
            papers = pickle.load(f)
    else:
        if args.year >= 2000: args.year -= 2000
    
        papers = get_papers(
            year=args.year, month=args.month, 
            start_code=args.start_code, end_code=args.end_code,
            filter_category=args.filter_category, filter_author=args.filter_author
        )
        with open(f"papers_{args.year}{str(args.month).zfill(2)}.{args.start_code}-{args.end_code}.pkl", "wb") as f:
            pickle.dump(papers, f)
    print("Done.")
    
    # separate by date
    date_set = set()
    date_papers = dict()
    for k, v in papers.items():
        date_set.add(v["date"])
        if v["date"] not in date_papers:
            date_papers[v["date"]] = list()
        date_papers[v["date"]].append((k, v))

    # tkinter
    def add_item():
        for date in sorted(date_set):
            listbox1.insert(tk.END, date)

    def on_select(event):
        selected_index = listbox1.curselection()
        if selected_index:
            listbox2.delete(0, tk.END)

            selected_item = listbox1.get(selected_index[0])
            for k, v in date_papers[selected_item]:
                listbox2.insert(tk.END, k)

    def on_select2(event):
        selected_index = listbox2.curselection()
        if selected_index:
            title_entry.delete(0, tk.END)
            author_entry.delete(0, tk.END)
            category_entry.delete(0, tk.END)
            url_entry.delete(0, tk.END)
            abstract_box.delete(1.0, tk.END)

            selected_item = listbox2.get(selected_index[0])
            paper = papers[selected_item]
            title_entry.insert(tk.END, paper["title"])
            author_entry.insert(tk.END, paper["authors"])
            category_entry.insert(tk.END, paper["categories"] + ["primary: " + paper["primary_category"]])
            url_entry.insert(tk.END, paper["url"])
            abstract_box.insert(tk.END, paper["abstract"])

    def download_button_click():
        url = url_entry.get() + ".pdf"
        title = url.split("/")[-1]
        download_pdf(url, f"{title}")

    def translate_button_click():
        abstract = abstract_box.get(1.0, tk.END)
        result = translator.translate(abstract, tgt_lang_code)
        abstract_box.delete(1.0, tk.END)
        abstract_box.insert(tk.END, result.text)

    def prev_button_click():
        selected_index = listbox2.curselection()
        if selected_index:
            selected_item = listbox2.get(selected_index[0])
            paper = papers[selected_item]
            abstract_box.delete(1.0, tk.END)
            abstract_box.insert(tk.END, paper["abstract"])

    # Root window
    root = tk.Tk()

    root.geometry('800x600')
    root.title('GUI Example')
    root.resizable(False, False)

    # Listbox 1
    list_label = tk.Label(root, text='Date')
    list_label.place(x=27, y=8)
    listbox1 = tk.Listbox(root)
    listbox1.place(x=10, y=30, width=73, height=500)
    scrollbar1 = tk.Scrollbar(root, orient='vertical')
    scrollbar1.config(command=listbox1.yview)
    scrollbar1.place(x=83, y=30, height=500)
    listbox1.config(yscrollcommand=scrollbar1.set)
    pixelVirtual = tk.PhotoImage(width=1, height=1)
    update_button = tk.Button(root, text='Update', command=add_item, width=56, height=50, image=pixelVirtual, compound='c')
    update_button.place(x=10, y=535)
    listbox1.bind("<<ListboxSelect>>", on_select)

    # Listbox 2
    paper_label = tk.Label(root, text='Code')
    paper_label.place(x=123, y=8)
    listbox2 = tk.Listbox(root)
    listbox2.place(x=103, y=30, width=73, height=500)
    scrollbar2 = tk.Scrollbar(root, orient='vertical')
    scrollbar2.config(command=listbox2.yview)
    scrollbar2.place(x=176, y=30, height=500)
    listbox2.config(yscrollcommand=scrollbar2.set)
    listbox2.bind("<<ListboxSelect>>", on_select2)

    # Title Label and Entry
    title_label = tk.Label(root, text='Title')
    title_label.place(x=222, y=30)
    title_entry = tk.Entry(root)
    title_entry.place(x=251, y=30, width=523)

    # Author Label and Entry
    author_label = tk.Label(root, text='Author')
    author_label.place(x=207, y=50)
    author_entry = tk.Entry(root)
    author_entry.place(x=251, y=50, width=523)

    # Category Label and Entry
    category_label = tk.Label(root, text='Category')
    category_label.place(x=196, y=70)
    category_entry = tk.Entry(root)
    category_entry.place(x=251, y=70, width=523)

    # url Label and Entry
    url_label = tk.Label(root, text='URL')
    url_label.place(x=223, y=90)
    url_entry = tk.Entry(root)
    url_entry.place(x=251, y=90, width=523)
    download_button = tk.Button(root, text='Download', command=download_button_click, width=56, height=20, image=pixelVirtual, compound='c')
    download_button.place(x=710, y=110)

    # abstract Text Box
    abstract_label = tk.Label(root, text='Abstract')
    abstract_label.place(x=250, y=140)
    abstract_box = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    abstract_box.place(x=251, y=160, width=539, height=370)
    pixelVirtual2 = tk.PhotoImage(width=1, height=1)
    prev_button = tk.Button(root, text='Original', width=56, height=50, image=pixelVirtual2, compound='c', command=prev_button_click)
    prev_button.place(x=251, y=535)
    pixelVirtual3 = tk.PhotoImage(width=1, height=1)
    translate_button = tk.Button(root, text='Translate', width=56, height=50, image=pixelVirtual3, compound='c', command=translate_button_click)
    translate_button.place(x=710, y=535)

    root.mainloop()