from flask import Flask, render_template, request
from flask_cors import cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from connection import *
from logger import *

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SECRET_KEY"] = 'ed93a0fd1f3fca263d3c915fa9bc4ccc28c4c30b0e814a3e01972fcad1f09a51'


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            qry = """
                use product_reviews;
                CREATE TABLE {searchString} (Product VARCHAR(255), 
                Customer_Name VARCHAR(255),
                Rating int, 
                Heading VARCHAR(255), 
                Comment VARCHAR(255))
            """
            qry = qry.format(searchString=searchString)
            cursor.execute(qry)
            log.info(f"{searchString} table created in database")
            reviews = []
            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except KeyError:
                    name = 'No Name'

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text
                except KeyError:
                    rating = 'No Rating'

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text
                except KeyError:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    log.error("Exception while creating dictionary: %s", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
                reviews = reviews[0:(len(reviews) - 1)]

                for i in reviews:
                    sql = """INSERT INTO {searchString} (Product, Customer_Name, Rating, Heading, Comment) VALUES (%s, 
                                                    %s, %d, %s, %s) 
                                                    """
                    val = (i["Product"], i["Name"], i["Rating"], i["CommentHead"], i["Comment"])
                    cursor.execute(sql, val)
                log.info("data stored in database")
            return render_template('results.html', reviews=reviews)

        except Exception as e:
            log.error(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
