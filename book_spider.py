import requests
from lxml import etree
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_url_function(url):
    '''
    获取页面，如果失败进行重试（最多三次重试）
    '''
    try_time = 0
    while try_time < 3:
        try:
            returner = requests.get(url, timeout=5)
            return returner
        except:
            print("错误！正在重试（第{}次）......".format(try_time + 1))
            try_time += 1
    print("错误！请检查网络设置")


chrome_options = webdriver.ChromeOptions()
# 使用headless无界面浏览器模式
chrome_options.add_argument('--headless') 
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)

# 以"http://www.xbiquge.la/"作为爬取网站
base_url = "http://www.xbiquge.la/"
driver.get(base_url) # 获取网站页面
searcher = driver.find_element_by_id("wd") # 查找输入框

search_bottom = driver.find_element_by_id("sss") # 查找“搜索”按钮

search_command = input("请输入想要搜索的书名:")
searcher.send_keys(search_command) 
search_bottom.click()
# 模拟输入并搜索

data_undealt = driver.page_source

data_after_tree = etree.HTML(data_undealt) # 加载

# 获取搜索结果中的书名、作者、对应的url
book_names = data_after_tree.xpath('//form[@method="post" and @name="checkform"]/table/tbody/tr/td[@class="even"]/a/text()')
book_urls = data_after_tree.xpath('//form[@method="post" and @name="checkform"]/table/tbody/tr/td[@class="even"]/a/@href')

writers = data_after_tree.xpath('//form[@method="post" and @name="checkform"]/table/tbody/tr/td[@class="even"]/text()')

books = zip(book_names, book_urls, writers)

template = "{0:{3}^5}{1:{3}^25}{2:^15}" # 输出模版，顺序为 编号 书名 作者

counter = 1

temp_books = [] # 用于将books内的所有内容放在列表中，方便直接查找

# 输出书名和作者
print(template.format("编号", "书名", "作者", chr(12288)))
print("================================================================================")
for i in books:
    temp = []
    print(template.format(str(counter), i[0], i[2], chr(12288)))
    temp.append(str(counter))
    temp.append(i[0])
    temp.append(i[1])
    temp_books.append(temp)
    counter += 1

exit_flag = False

while True:
    # 接受书的编号，try用于避免错误编号导致崩溃
    try:
        get_book_number = int(input("请输入需要获取的书的编号（输入-1退出）:"))
        if not get_book_number < counter and get_book_number >= -1:
            print("命令错误!")
            print("请重新输入")
        elif get_book_number == -1:
            # 退出
            print("退出")
            exit_flag = True
            break
        else:
            break
    except:
        print("错误!")

if exit_flag == True:
    # 判断是否退出
    driver.quit()
    exit()


# 安装编号获取书的章节目录
get_book_url = temp_books[get_book_number - 1][2]
get_book_name_file = temp_books[get_book_number - 1][1]
driver.get(get_book_url)
get_book_page = driver.page_source

basic = "http://www.xbiquge.la"

# 获取每一章的名称和url
get_data = etree.HTML(get_book_page)
get_titles = get_data.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/text()')
get_book_content_url = get_data.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')

get_content = zip(get_titles, get_book_content_url)

# 设置进度条
bar = tqdm(total=len(get_titles), desc='获取进度', leave=True, ncols=100, unit='章', unit_scale=True)

print("开始获取{}，获取时间可能较长，请稍安勿躁".format(get_book_name_file))

# 打开文件，并开始获取内容
with open("./{}.txt".format(get_book_name_file), "w") as f:
    for i in get_content:
        # 更新进度条
        bar.update()
        # 使用requests获取页面内容
        response = get_url_function(basic + i[1])
        response.encoding='utf-8'
        ddata = etree.HTML(response.text)
        f.write("\n=====================================================\n")
        f.write(i[0])
        f.write("\n=====================================================\n")
        contents = ddata.xpath('//div[@class="box_con"]/div[@id="content"]/text()')
        # 写入文件
        for j in contents:
            f.write(j)
print("获取成功!")
 
driver.quit()
