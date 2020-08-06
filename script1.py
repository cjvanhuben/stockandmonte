from flask import Flask, request, render_template

from bokeh.resources import CDN
import random
from scipy.stats import norm
import math
import pandas as pd
from pandas_datareader import data
import datetime
import numpy as np
from datetime import date
from bokeh.plotting import figure,show
from bokeh.embed import components,file_html
from bokeh.models import Label, Title, NumeralTickFormatter,LinearAxis, Range1d,HoverTool,Panel,Tabs


app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def plot():
    # from bokeh.io import vform

    end = date.today()
    # start = datetime.datetime.now() - datetime.timedelta(days=900)

    tickername = 'TSLA'
    if request.method =='POST':
        tickername = request.form['inputticker']
        tickername = tickername.upper()


        if tickername == '':
            tickername = 'TSLA'


    def getData(tickername=tickername):
        try:
            df = data.DataReader(name=tickername,data_source="yahoo",start=0,end=date.today())
            return df
        except:
            tickername = 'TSLA'
            df = data.DataReader(name=tickername,data_source="yahoo",start=0,end=date.today())
            return df

    def getsp():
        return data.DataReader(name='^GSPC',data_source = 'yahoo',start = 0, end = end)

    def createGraph(df,sp,start,end,tickername=tickername):

        def inc_dec(c,o):
            if c>o:
                return "Increase"
            elif c<o:
                return "Decrease"
            else:
                return "Equal"

        df["Status"] = [inc_dec(c,o) for c,o in zip(df.Close,df.Open)]
        df["Middle"] = (df.Open+df.Close)/2
        df['Spread'] = abs(df.Open-df.Close)


        hours_12=12*60*60*1000

        p = figure(x_axis_type='datetime',width=1000,height=500,sizing_mode='scale_width')

        p.add_tools(HoverTool(
            tooltips=[
                ('Date','$x{%F}'),
                ('Price','$y{($0.00)}')

            ],

            formatters={
                '$x':'datetime', # use 'datetime' formatter for '@date' field

            },

            # display a tooltip whenever the cursor is vertically in line with a glyph
            mode='vline'
        ))
        # p.title.text=tickername
        p.grid.grid_line_alpha=.3


        #setting the range with what is in the tab

        dfrange = df.loc[start:end]
        sprange = sp.loc[start:end]

        p.y_range = Range1d(dfrange.Low.min(),dfrange.High.max())
        p.x_range= Range1d(dfrange.index.min(),dfrange.index.max())
        p.extra_y_ranges = {"foo": Range1d(start=sprange.Low.min(),end=sprange.High.max())}
        p.add_layout(LinearAxis(y_range_name="foo"),'right')


        p.line(sp.index,sp.Close,line_width=1,line_color = 'blue',y_range_name="foo",legend_label = 'S&P 500')
        p.segment(df.index,df.High,df.index,df.Low,color='black',legend_label = tickername)

        p.rect(df.index[df.Status =='Increase'],df.Middle[df.Status=='Increase'], hours_12,df.Spread[df.Status=='Increase'],fill_color='green',line_color='black',width = 500)

        p.rect(df.index[df.Status == 'Decrease'],df.Middle[df.Status=='Decrease'], hours_12,df.Spread[df.Status=='Decrease'],fill_color='#FF3333',line_color='black', width = 500)


        return p

    df = getData(tickername)
    sp=getsp()
    oneweekgraph = createGraph(df,sp,datetime.datetime.now() - datetime.timedelta(days=7),end)
    onemonthgraph = createGraph(df,sp,datetime.datetime.now() - datetime.timedelta(days=30),end)
    # threemonthgraph = createGraph(datetime.datetime.now() - datetime.timedelta(days=90),end)
    sixmonthgraph = createGraph(df,sp,datetime.datetime.now() - datetime.timedelta(days=180),end)
    oneyeargraph = createGraph(df,sp,datetime.datetime.now() - datetime.timedelta(days=365),end)
    # threeyeargraph = createGraph(datetime.datetime.now() - datetime.timedelta(days=1090),end)
    fiveyeargraph = createGraph(df,sp,datetime.datetime.now() - datetime.timedelta(days=1825),end)


    tab1=Panel(child=oneweekgraph,title='1 Week')
    tab2=Panel(child=onemonthgraph,title='1 Month')
    # tab3=Panel(child=threemonthgraph,title='3 Months')
    tab4=Panel(child=sixmonthgraph,title='6 Months')
    tab5=Panel(child=oneyeargraph,title='1 Year')
    # tab6=Panel(child=threeyeargraph,title='3 Years')
    tab7=Panel(child=fiveyeargraph,title='5 Years')

    df=getData(tickername)
    smalldf = df[-5:][['Open','Adj Close']]
    smalldf['SortDate'] = pd.to_datetime(smalldf.index)
    smalldf.sort_values(by=['SortDate'],inplace=True,ascending=False)
    smalldf = smalldf.drop(columns='SortDate')
    stocktable = smalldf.to_html(col_space= '160px',justify='center',index_names=False,float_format=lambda x: '$%10.2f' % x)


    tabs=Tabs(tabs=[tab1,tab2,tab4,tab5,tab7])

    script1,div1=components(tabs)


    # show(p)
    cdn_js0=CDN.js_files[0]
    cdn_js1=CDN.js_files[1]
    cdn_js2=CDN.js_files[2]
    cdn_js3=CDN.js_files[3]



    return render_template("index.html",script1 = script1,div1=div1,cdn_js0=cdn_js0,cdn_js1=cdn_js1,tickername = tickername,stocktable=stocktable,cdn_js2=cdn_js2,cdn_js3=cdn_js3)

@app.route('/monte', methods=['GET','POST'])
def monte():
    tickers=[]
    amounts = []
    if request.method =='POST':
        # tickername = request.form['inputticker']

        for x in range(1,11):
            if (request.form["ticker%s" %x]):
                tickers.append(request.form["ticker%s" %x])
                if not(request.form["amount%s" %x]):
                    amounts.append(0)
                else:
                    amounts.append(request.form["amount%s" %x])
        def getHistory(tickers):
            historicals = []
            for ticker in tickers:

                try:

                    df = data.DataReader(name=ticker,data_source="yahoo",start=0,end=date.today())


                except:
                    ticker = '^GSPC'
                    df = data.DataReader(name=ticker,data_source="yahoo",start=0,end=date.today())

                df["Dif"] = df["Adj Close"].div(df["Adj Close"].shift(1))
                df["Daily Returns"] = np.log(df["Dif"])
                print(df)

                average = df['Daily Returns'].mean()
                print(average)
                variance=df['Daily Returns'].var()
                print(variance)
                drift = average-(variance/2)
                std = df['Daily Returns'].std()
                inv = norm.ppf(random.uniform(0,1))
                ran = std*inv
                print(drift)
                print(ran)
                historicals.append(drift)

                historicals.append(ran)

                return historicals


        stock =dict(zip(tickers,getHistory(tickers)))










    # print(stock.get('tsla'))



    return render_template("monte.html")

# @app.route('/')
# def home():
#     return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
