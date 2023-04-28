from flask import Flask, render_template, request
from config import configs
from tools.code_checking import code_cheching
from tools.code_searching import code_recommendation
import os
from datetime import timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
code_recommendation_object = code_recommendation(configs())


json_data= []
@app.route('/', methods=['GET', 'POST'])

@app.route('/index', methods=['GET', 'POST'])
def index():
    print('kg loading has done')
    print('start to loading datas into session...')
    return render_template('index.html')

@app.route('/searchname',methods=['GET', 'POST'])    #选择TASK页面
def searchname():
    return render_template("searchname.html")

@app.route('/code_checking',methods=['GET', 'POST'])   #输入code页面
def code_checking():
    return render_template("code_checking.html")

@app.route('/code_checking_detail',methods=['GET', 'POST'])   #显示一系列函数页面
def code_checking_detail():
    if request.method == 'POST':
        code = request.form.get("search")
        code_cheching_object = code_cheching(configs())
        results = code_cheching_object.get_checking_results(code)
        # print(results)
        return render_template("code_checking_detail.html",results=results)

@app.route('/code_checking_name',methods=['GET', 'POST'])    #显示代码检错页面
def code_checking_name():
        return render_template("code_checking_name.html")


@app.route('/code_searching',methods=['GET', 'POST'])    #输入自然语言页面
def code_searching():
    return render_template("code_searching.html")

@app.route('/code_searching_name',methods=['GET','POST'])    #显示代码搜索页面
def code_searching_name():
    if request.method == 'POST':
        return render_template("code_searching_name.html")

@app.route('/code_searching_detail',methods=['GET','POST'])    #显示代码搜索页面
def code_searching_detail():
    if request.method == 'POST':

        query = request.form.get("search")
        results = code_recommendation_object.search(query)
        results = json.dumps(results)
        # print(results)
        return render_template("code_searching_detail.html",results=results)

@app.route('/<int:id>',methods=['GET', 'POST'])   #代码检错，查看详情
def show_detail(id):
    with open("tools/Templefile.json", 'r', encoding='utf-8') as f:
        json_data = json.load(f)

        id = int(id)
        # vulnerable
        if json_data["result"][id]["type"] == 1:
            results = {}
            results["result"] = json_data["result"][id]["results"]
            new_results = json.dumps(results)

            return render_template("code_checking_name.html",results = new_results)
        #safe
        else:
            show_detail_list = json_data["result"][id]["MoreDetails"]
            results = {}
            results["all"] = show_detail_list
            new_results = json.dumps(results)
            # show safe functions
            return render_template("show_detail_id.html",results=new_results)

@app.route('/<int:id1>result<int:id2>',methods=['GET', 'POST'])   #显示流程图代码
def show_flow_chat(id1,id2):
    with open("tools/Templefile.json", 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    id1 = int(id1)
    id2 = int(id2)
    # print(id1,id2)
    graph_data = {}
    graph_data["entities"] = json_data["result"][id1]["results"][id2]["graph"]
    graph_data["links"] = json_data["result"][id1]["results"][id2]["graph_index"]
    print(graph_data)
    graph_data = json.dumps(graph_data)
    return render_template("flow_chat.html",graph_data=graph_data)  #单纯显示流程图页面

@app.route('/<int:id>detail',methods=['GET', 'POST'])
def show_code_searching_details(id):

    result = code_recommendation_object.get_a_result_by_entity_id(id)
    result = json.dumps(result)
    return render_template("show_code_searching_detail.html",result=result)

@app.route('/<int:id>searchchat',methods=['GET', 'POST'])
def show_code_searching_chat(id):

    result = code_recommendation_object.get_a_result_by_entity_id(id)

    graph_data = {}
    graph_data["entities"] = result["graph"]
    graph_data["links"] = result["graph_index"]
    graph_data = json.dumps(graph_data)
    # show the execution
    return render_template("flow_chat.html", graph_data=graph_data)

if __name__ == '__main__':

    app.debug = True
    app.run()
