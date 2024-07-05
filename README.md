# arxiv-crawling
This arxiv crawling program is a useful and allows you to quickly browse abstracts and download papers of interest. 
It is made with simple codes and is easy to use.

## Install

1. Clone the whole repo.
    ```bash
    $ git clone {repo_url}
    ```

1. Setup a virtual environment.
    ```bash
    $ conda create -n arxiv python=3.8 -y
    $ conda activate arxiv
    ```

1. Install python packages in `requirements.txt`.
    ```bash
    $ cd arxiv-crawling
    $ pip install -r requirements.txt
    ```

## How to run get_paper.py

### Get papers using GUI
```bash
$ python get_paper.py -y YYYY -m MM -s {start_number_code} -e {end_number_code} -fc {category_for_filter} {optional: -fa {author_for_filter} -p {data_path}}
```

- YYYY: Input the year what you want to get.
- MM: Input the month what you want to get.
- {start_number_code}: At least 0, but not limited.
- {end_number_code}: The most recent paper code uploaded to arxiv. You can find in https://arxiv.org.
- {category_for_filter}: What you want to get paper category.

[optional]
- {author_for_filter}: not implement perfectly.
- {data_path}: This is ".pkl" file path for previously obtained papers, and can be obtained by running it once.


For example, 
```bash
$ python get_paper.py -y 2024 -m 7 -s 0 -e 1000 -fc cs
$ python get_paper.py -y 2024 -m 7 -s 0 -e 1000 -fc cs.AI
```

## GUI
1. When get papers complete, you can update the paper list using **Update button**.
2. You can see the Title, Author, Category, URL, Abstract when you click **paper code**.
3. Also, you can download paper using **Download button**, and it can be translate your langauge using **Translate button**.
4. **Original button** features that return the translated text to english text.

![gui](https://github.com/jinsikbang/arxiv-crawling/assets/110602334/280f7071-67f4-41bd-82d0-45d087509506)

## Additional Info.
In get_paper.py, if you don't live in South Korea, you should change your location time.

Make sure your location time to fit in https://arxiv.org.

``` python
13  EST = -5                  # -5 should be changed
14  def get_time(location=9): #  9 should be changed
15      t = time.time() - (location * 3600) + (EST * 3600)
16      tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, _, _, _ = time.localtime(t)
17      return tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec
```

If you want to change translate language, you should change the 94 line in get_papers.py
``` python
93  translator = Translator()
94  tgt_lang_code = "ko"      # You should change the code to where you live
95  tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec = get_time()
```
