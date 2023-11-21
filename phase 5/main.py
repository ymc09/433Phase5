from flask import Flask,request, render_template
import psycopg2
import base64
app = Flask(__name__) #create instance of flask
conn = psycopg2.connect(
   database="FOUR3THREE", user='postgres', 
   password='Ay0oy@EECE433', host='127.0.0.1', port= '5432'
)

@app.route("/", methods=['POST','GET']) 
def main():
    cursor=conn.cursor()
    ################### Discounted items
    query="""
        SELECT distinct on (c1."clothing_name") c1."clothing_name","clothing_price","clothing_discount","clothing_photos" 
        from "Clothing/Accessory item name" as c1,"Photos Clothing" as c2,"Clothing/Accessory item" as c3 where 
        c3."clothing_RefNb"=c2."clothing_RefNb" and c1."clothing_name"=c3."clothing_name"  
        and c3."clothing_RefNb" in (select "clothing_RefNb" from "Clothing/Accessory item" as ca1, "Clothing/Accessory item name" as ca2 where ca1."clothing_name"=ca2."clothing_name" order by "clothing_discount" desc limit 10)
        """
    cursor.execute(query)
    discounted_items=cursor.fetchall()
    print(discounted_items)
    for i in range(len(discounted_items)):
        discounted_items[i]=list(discounted_items[i])
        discounted_items[i][1]=round(discounted_items[i][1],2)
        discounted_items[i].append(round(discounted_items[i][1]/(1-discounted_items[i][2]),2)) # adding original price
        discounted_items[i][2]=discounted_items[i][2]*100
    discounted_items.sort(key=lambda T:T[2])
    discounted_items=discounted_items[::-1]
    query="""SELECT distinct on (C1."clothing_name") C1."clothing_name",C2."clothing_price",C2."clothing_discount", "clothing_photos" from "Clothing/Accessory item" as C1, "Clothing/Accessory item name" as C2,
            "Photos Clothing" as Ph where C1."clothing_name"=C2."clothing_name" and C1."clothing_RefNb"=Ph."clothing_RefNb"
            and C1."clothing_RefNb" in (select O."clothing_RefNb" from "Ordered By Clothing" as O group by(O."clothing_RefNb") order by(count(*)) desc);
            """
    ###################### Best Sellers
    cursor.execute(query)
    best_sellers=cursor.fetchall()

    for i in range(len(best_sellers)):
        best_sellers[i]=list(best_sellers[i])
        best_sellers[i][1]=round(best_sellers[i][1],2)
        best_sellers[i].append(round(best_sellers[i][1]/(1-best_sellers[i][2]),2)) # adding original price
        best_sellers[i][2]=best_sellers[i][2]*100
    print(best_sellers)
    search_query=request.form.get("search_bar")
    search_results_cloth=[]
    search_results_cos=[]
    ###################### Search 
    search=False
    if search_query!=None and search_query!='':
        query='(SELECT distinct on (C1."clothing_name") C1."clothing_name",C2."clothing_price",C2."clothing_discount", "clothing_photos" from "Clothing/Accessory item name" as C2,"Clothing/Accessory item" as C1,"Photos Clothing" as Ph where C2."clothing_name"=C1."clothing_name" and C1."clothing_RefNb"=Ph."clothing_RefNb" and  ("main_type" like'+"'%"+search_query+"%'"+'or "sub_type" like'+"'%"+search_query+"%'"+'or "clothing_description" like'+"'%"+search_query+"%'"+' or C1."clothing_name" like'+"'%"+search_query+"%'"+ "))" 
        print(query)
        cursor.execute(query)
        search_results_cloth=cursor.fetchall()
        query='(SELECT distinct on ("cosmetic_name") "cosmetic_name","cosmetic_price","cosmetic_discount", "cosmetic_photos" from "Cosmetic item" as i,"Photos Cosmetic" as p where i."cosmetic_RefNb"=p."cosmetic_RefNb" and ("cosmetic_name" like'+"'%"+search_query+"%'"+'or "cosmetic_description" like'+"'%"+search_query+"%'))"
        print(query)
        cursor.execute(query)
        search_results_cos=cursor.fetchall()
        best_sellers=[]
        discounted_items=[]
        for i in range(len(search_results_cloth)):
            search_results_cloth[i]=list(search_results_cloth[i])
            search_results_cloth[i][1]=round(search_results_cloth[i][1],2)
            search_results_cloth[i].append(round(search_results_cloth[i][1]/(1-search_results_cloth[i][2]),2)) # adding original price
            search_results_cloth[i][2]=search_results_cloth[i][2]*100
        for i in range(len(search_results_cos)):
            search_results_cos[i]=list(search_results_cos[i])
            search_results_cos[i][1]=round(search_results_cos[i][1],2)
            search_results_cos[i].append(round(search_results_cos[i][1]/(1-search_results_cos[i][2]),2)) # adding original price
            search_results_cos[i][2]=search_results_cos[i][2]*100
        search=True
    
    return render_template("main.html",discounted_items1=discounted_items[:len(discounted_items)//2],
                           discounted_items2=discounted_items[len(discounted_items)//2:],
                           best_sellers1=best_sellers[:len(best_sellers)//2],best_sellers2=best_sellers[len(best_sellers)//2:],
                           search_results_cloth=search_results_cloth,search_results_cos=search_results_cos,search=search)
if __name__ == "__main__":
    app.run()
