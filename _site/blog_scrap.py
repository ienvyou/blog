import os
import time
import requests
from bs4 import BeautifulSoup

# 티스토리 블로그에는 총 71개의 글이 있다. 중간에 빠진 글도 있을 수 있다.
# 주소 http://blog.osci.kr/4  마지막에 게시글 번호가 있다.
# 증분으로 크롤링을 해보겠다.
# 이미지는 다운로드 받아서 마크다운으로 대체한다.

# 헤더 설정(설정하지 않으면 티스토리에서 막는다.)
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}

for post_number in range(1, 72):
    try:
        time.sleep(3)
        print(f'http://blog.osci.kr/{post_number}')
        url = f'http://blog.osci.kr/{post_number}'
        # get 방식으로 호출
        r = requests.get(url, headers=headers)
        # bs(BeautifulSoup)로 맵핑
        soup = BeautifulSoup(r.text, 'html.parser')

        # body 맵핑
        body = soup.find("div", {"class", "area_view"})
        post_title = soup.find('meta', {'name': 'title'})['content']
        # 게시글 폴더 생성
        if not os.path.exists(f'./assets/images/{post_number}'):
            os.makedirs(f'./assets/images/{post_number}')

        # get image file name
        for img in body.find_all('img'):
            try:
                image_name = img['filename']
                image_src = img['src']
                # insert image markdown
                img.insert_after(
                    f'![{image_name}]' + '({{ ' + f'"/assets/images/{post_number}/{image_name}" | relative_url ' + '}})')
                print('downloading..', image_name, ', ', image_src)
                img_bin = requests.get(image_src, headers=headers)
                f = open(f'./assets/images/{post_number}/{image_name}', 'wb')
                f.write(img_bin.content)
                f.close()
                img.unwrap()
                time.sleep(1)
            except Exception as e:
                print(e)


        for p_tag in body.find_all('p'):
            if len(p_tag.text) > 0:
                p_tag.insert_before('#### ')
            p_tag.unwrap()

        post_header = '---\n'
        post_header += 'layout: post\n'
        post_header += f'title: {post_title}\n'
        post_header += 'date: 2018-06-25 09:15:36 +0900\n'
        post_header += 'categories: \n'
        post_header += 'author: OpenSourceConsulting\n'
        post_header += '---\n'

        print(post_header)

        post_file = open(f'./_posts/2018-06-25-tistory-{post_number}.markdown', 'w')
        post_file.write(post_header)
        post_file.write(body.get_text())
        post_file.close()
    except Exception as e:
        print(e)