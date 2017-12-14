# coding: UTF-8
from pyquery import PyQuery as pq
import re, json, time
import os.path

class GetMovieReview:
    #def __init__(self):
        #self.REVIEW_NUM_MAX = 5
        #self.REVIEW_RATING_MIN = 5 # 0-9

    def get_review(self, title, num, rating_min):
        '''
        Check if 'review' directory exists.
        '''
        if not os.path.isdir('review'):
            os.mkdir('review')

        self.REVIEW_NUM_MAX = num
        self.REVIEW_RATING_MIN = rating_min # 0-9

        item_id = self.search(title)
        if item_id != 0:
            print item_id
            result_num = self.access(item_id)

    # Search the query on IMDB
    def search(self, title):
        # http://www.imdb.com/find?ref_=nv_sr_fn&q=Star+Wars+:+The+Force+Awakens&s=tt
        replaced_title = self.replace_symbol(title)
        url = "http://www.imdb.com/find?ref_=nv_sr_fn&q=" + replaced_title + "&s=tt"
        query = pq(url, parser='html')

        try:
            item_top_url = query('table[class=\"findList\"]').children().children().eq(0).children('a').attr('href')
            reg_ex = re.compile("title/([a-z0-9]+)/")
            reg_ex_result = reg_ex.search(item_top_url)
            return reg_ex_result.group(1)
        except:
            print "Error: couldn't find this ... " + title
            return 0

    # Encoder
    def replace_symbol(self, query):
        # use these three lines to do the replacement
        rep = {
            "!": "%21",
            "*": "%2A",
            "'": "%27",
            "(": "%28",
            ")": "%29",
            ";": "%3B",
            ":": "%3A",
            "@": "%40",
            "&": "%26",
            "=": "%3D",
            "+": "%2B",
            "$": "%24",
            ",": "%2C",
            "/": "%2F",
            "?": "%3F",
            "%": "%25",
            "#": "%23",
            "[": "%5B",
            "]": "%5D",
            " ": "+"
        }
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        return pattern.sub(lambda m: rep[re.escape(m.group(0))], query)


    def access(self, item_id):
        #url = "http://www.imdb.com/title/tt1837492/"
        url = "http://www.imdb.com/title/" + item_id + "/"
        query = pq(url, parser='html')
        title = query('title').text()
        page_num_max = 0
        f_tmp = open('temp_review', 'w')
        review_output = ""
        review_tmp = ""

        print '{Title: ' + title + '}'

        imdb_rating = query('span[itemprop=\'ratingValue\']').text()
        print '{Rating: ' + imdb_rating + '}'

        url += 'reviews'
        query = pq(url, parser='html')

        pages = re.search(r'<font[^>]*?>(.+)</font>', str(query('table').eq(1)))
        if pages :
            pages = re.search(r'of(.+):', str(pages.group(1)))
            if pages : page_num_max = int(pages.group(1))
        print '{PageNumMax: ' + str(page_num_max) + '}\n'

        review_cnt = 0
        for num in range(page_num_max):
            #review(url, num*10)
            review_result = self.review(item_id, num*10, review_cnt)
            review_cnt = review_result[0]
            review_output += review_result[1]
            # Max review number = 100
            if review_cnt >= self.REVIEW_NUM_MAX: break
            time.sleep(1)

        f_tmp.write(review_output)
        f_tmp.close()

        return review_cnt


    def review(self, item_id, page, review_cnt):
        filename = 'review/' + item_id + '.json'
        f = open(filename, 'a')
        #f_tmp = open('temp_review', 'w')
        review_output = ""
        review_rating_num = 0
        url = "http://www.imdb.com/title/" + item_id + "/reviews"

        if page : url += '?start=' + str(page)
        query = pq(url, parser='html')
        review_title = []
        review_date = []
        review_rating = []
        review_content = []
        review_reviewer = []
        for tag in query('h2'):
            # Max review number = 100
            if review_cnt >= self.REVIEW_NUM_MAX: break
            # Ignore a review that doesn't have a rating
            if query(tag).next('img').attr('alt') is not None:
                review_title.append(query(tag).text())
                user = query(tag).prev('a').attr('href')
                user = re.sub('/user/', "", user)
                user = re.sub(r'/', "", user)
                review_reviewer.append(user)
                review_rating.append(query(tag).next('img').attr('alt'))
                tmp_rating = re.search(r'([0-9])/', str(query(tag).next('img').attr('alt')))
                review_rating_num = int(tmp_rating.group(1))

                '''
                Measure for a review that doesn't have a location data
                '''
                if query(tag).nextAll('small').eq(1).text() is not '':
                    review_date.append(query(tag).nextAll('small').eq(1).text())
                else:
                    review_date.append(query(tag).nextAll('small').eq(0).text())

                content = query(tag).parent('div').next('p').text()
                content = content.replace('\n','')
                content = content.replace('\r','')
                review_content.append(content)

                if review_rating_num > self.REVIEW_RATING_MIN:
                    print str(review_rating_num)
                    review_output += content.encode('utf-8') + '\n'

                    review_cnt += 1

        for num, item in enumerate(review_title):
            dict = {
                'itemID' : 'tt1837492',
                'reviewTitle' : review_title[num].encode('utf_8'),
                'reviewerId' : review_reviewer[num].encode('utf_8'),
                'reviewRating' : review_rating[num].encode('utf_8'),
                'reviewText' : review_content[num].encode('utf_8'),
                'reviewDate' : review_date[num].encode('utf_8')
            }
            json.dump(dict, f, indent=2)

        f.close()
        #f_tmp.close()
        return review_cnt, review_output

'''
if __name__ == '__main__':
    #main()
    method = GetMovieReview()
    method.get_review()
'''
