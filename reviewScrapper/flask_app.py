# doing necessary imports

from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq


app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
         # obtaining the search string entered in the form
        try:
            searchString = request.form['content'].replace(" ","")
            #dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            #db = dbConn['crawlerDB'] # connecting to the database called crawlerDB
            #reviews = db[searchString].find({}) # searching the collection with the name same as the keyword
            #if reviews.count() > 0: # if there is a collection with searched keyword and it has records in it
                #return render_template('results.html',reviews=reviews) # show the results to user
            #else:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)  # requesting the webpage from the internet
            flipkartPage = uClient.read()  # reading the webpage
            uClient.close()  # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser")  # parsing the webpage as HTML

            bigboxes = flipkart_html.findAll("div", {"class": "_1UoZlX"})

            box = bigboxes[0]

            product_link = box.a['href']

            productLink = flipkart_url + product_link
            prodRes = requests.get(productLink)
            prod_html = bs(prodRes.text, "html.parser")
            baseurl = 'https://www.flipkart.com'
            all_rev_link = prod_html.find('div', {'class': "swINJg _3nrCtb"})
            all_rev_link = all_rev_link.find_parent().get('href')
            #table = db[searchString]
            # filename = searchString + ".csv"
            # fw = open(filename, "w")
            # headers = "Product, Customer Name, Rating, Heading, Comment \n"
            # fw.write(headers)
            reviews = []

            i = 1
            url = baseurl + all_rev_link + '&page=' + str(i)
            while True:

                all_review_page = requests.get(url)
                all_review_html = bs(all_review_page.text, "html.parser")
                container_full = all_review_html.find('div', {'class': 'ooJZfD _2oZ8XT col-9-12'})
                review_container = all_review_html.findAll('div', {'class': 'col _390CkK _1gY8H-'})
                next_Page_Text = container_full.find('nav', {'class': '_1ypTlJ'}).findAll('span')[-1].text
                for review in review_container:
                    try:
                        name = review.findAll('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = 'No name'
                    try:
                        rating = review.findAll('div', {
                            'class': ['hGSR34 E_uFuv', 'hGSR34 _1x2VEC E_uFuv', 'hGSR34 _1nLEql E_uFuv']})[0].text
                    except:
                        rating = 'No rating'
                    try:
                        commentHead = review.findAll('p', {'class': '_2xg6Ul'})[0].text
                    except:
                        commentHead = 'No Comment Header'
                    try:
                        custComment = review.findAll('div', {'class': ''})[0].text
                    except:
                        custComment = 'No Comment'
                    mydict = {"Product": searchString,"Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}  # saving that detail to a dictionary
                    #x = table.insert_one(mydict)
                    reviews.append(mydict)

                if (next_Page_Text == 'Next'):
                    i = i + 1
                    url = baseurl + all_rev_link + '&page=' + str(i)
                else:
                    break
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')
if __name__ == "__main__":
    #app.run(port=8000,debug=True) # running the app on the local machine on port 8000
    app.run(debug=True)