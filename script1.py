from flask import Flask, request, render_template

from bokeh.resources import CDN

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def plot():
    import pandas as pd
    from pandas_datareader import data
    import datetime
    from datetime import date
    from bokeh.plotting import figure,show
    from bokeh.embed import json_item,components,file_html
    from bokeh.models import Label, Title, NumeralTickFormatter,LinearAxis, Range1d,HoverTool

    import json

    start = datetime.datetime.now() - datetime.timedelta(days=365)
    end = date.today()


    tickername = 'TSLA'
    if request.method =='POST':

        tickername = request.form['inputticker']
        tickername = tickername.upper()

        if tickername == '':
            tickername = 'TSLA'

    try:
        df = data.DataReader(name=tickername,data_source="yahoo",start=start,end=end)
    except:
        tickername = 'TSLA'
        df = data.DataReader(name=tickername,data_source="yahoo",start=start,end=end)

    sp = data.DataReader(name='^GSPC',data_source = 'yahoo',start = start, end = end)
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


    smalldf = df[-5:][['Open','Adj Close']]
    stocktable = smalldf.to_html(col_space= '160px',justify='center',index_names=False,float_format=lambda x: '$%10.2f' % x)

    hours_12=12*60*60*1000

    # print(sp.index)
    # tool = [
    # ('Date: ','$x'),
    # ('Price: ','$y')
    #
    # ]


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
    # p.yaxis[0].formatter = NumeralTickFormatter(format='$0,0')

    p.y_range = Range1d(df.Close.min(),df.Close.max())

    p.line(sp.index,sp.Close,line_width=1,line_color = 'blue',y_range_name="foo",legend_label = 'S&P 500')
    p.segment(df.index,df.High,df.index,df.Low,color='black',legend_label = tickername)

    p.rect(df.index[df.Status =='Increase'],df.Middle[df.Status=='Increase'], hours_12,df.Spread[df.Status=='Increase'],fill_color='green',line_color='black',width = 500)

    p.rect(df.index[df.Status == 'Decrease'],df.Middle[df.Status=='Decrease'], hours_12,df.Spread[df.Status=='Decrease'],fill_color='#FF3333',line_color='black', width = 500)

    p.extra_y_ranges = {"foo": Range1d(start=sp.Close.min(),end=sp.Close.max())}
    # p.yaxis.formatter = NumeralTickFormatter(format='$0,0')
    # p.extra_y_ranges.formatter = NumeralTickFormatter(format = '$0,0')



    p.add_layout(LinearAxis(y_range_name="foo"),'right')
    script1,div1=components(p)

    # show(p)
    cdn_js=CDN.js_files[0]
    # kwargs = {'plot_script': script1, 'plot_div': div1}
    # if request.method == 'GET':
    #     return render_template("index.html",**kwargs)

    # print(cdn_js)
    #
    # print(json_item(p))
    # print(script1)
    # print(div1)

    return render_template("index.html",script1 = script1,div1=div1,cdn_js=cdn_js,tickername = tickername,stocktable=stocktable)

# @app.route('/')
# def home():
#     return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
