from flask import Flask,request,redirect, render_template, flash, session
from datetime import datetime
import psycopg2
import base64
app = Flask(__name__) #create instance of flask
app.secret_key = 'FOUR33'
conn = psycopg2.connect(
   database="FOUR3THREE", user='postgres', 
   password='-----', host='127.0.0.1', port= '5432'
)
@app.route('/<product_id>')
def product(product_id):
    cursor=conn.cursor()
    # Find the product with the specified ID
    cursor.execute('(select "cosmetic_name","cosmetic_price","cosmetic_description","cosmetic_RefNb" from "Cosmetic item" where "cosmetic_name"='+"'"+product_id+"')")
    cosmetics=cursor.fetchall()
    cursor.execute('(select C1."clothing_name","clothing_price","clothing_description","clothing_RefNb","clothing_discount" from "Clothing/Accessory item" as C1, "Clothing/Accessory item name" as C2 where C1."clothing_name"=C2."clothing_name" and C1."clothing_name"='+"'"+product_id+"') union"+'(select "cosmetic_name","cosmetic_price","cosmetic_description","cosmetic_RefNb","cosmetic_discount" from "Cosmetic item" where "cosmetic_name"='+"'"+product_id+"')")
    product = list(cursor.fetchall()[0])
    product[1]=round(product[1],2)
    size=[]
    product.append(round(product[1]/(1-product[4]),2)) # adding original price
    product[4]=product[4]*100
    if len(cosmetics)==0:
        cursor.execute('select "size" from "Clothing/Accessory item" where "clothing_RefNb"='+"'"+str(product[3])+"'")
        size=cursor.fetchall()
        cursor.execute('(select * from "Photos Clothing" where "clothing_RefNb"='+str(product[3])+")")
    else:
        cursor.execute('select * from "Photos Cosmetic" where "cosmetic_RefNb"='+str(product[3]))
    pics=cursor.fetchall()
    return render_template('product_detail.html', product=product,pics=pics,size=size)

    
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
    search_query=request.form.get("search_bar")
    search_results_cloth=[]
    search_results_cos=[]
    ###################### Search 
    search=False
    if search_query!=None and search_query!='':
        query='(SELECT distinct on (C1."clothing_name") C1."clothing_name",C2."clothing_price",C2."clothing_discount", "clothing_photos" from "Clothing/Accessory item name" as C2,"Clothing/Accessory item" as C1,"Photos Clothing" as Ph where C2."clothing_name"=C1."clothing_name" and C1."clothing_RefNb"=Ph."clothing_RefNb" and  ("main_type" like'+"'%"+search_query+"%'"+'or "sub_type" like'+"'%"+search_query+"%'"+'or "clothing_description" like'+"'%"+search_query+"%'"+' or C1."clothing_name" like'+"'%"+search_query+"%'"+ "))" 
        cursor.execute(query)
        search_results_cloth=cursor.fetchall()
        query='(SELECT distinct on ("cosmetic_name") "cosmetic_name","cosmetic_price","cosmetic_discount", "cosmetic_photos" from "Cosmetic item" as i,"Photos Cosmetic" as p where i."cosmetic_RefNb"=p."cosmetic_RefNb" and ("cosmetic_name" like'+"'%"+search_query+"%'"+'or "cosmetic_description" like'+"'%"+search_query+"%'))"
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


cart=[]
cart.append(([5,'ddd','L',3,1]))
cart.append(([5,'ddd','L',3,1]))
cart.append(([5,'ddd','L',3,1]))
@app.route("/cart/addtocart/<int:product_id>", methods=['POST','GET']) 
def addToCart(itemRefNo):
    
        cursor=conn.cursor()
        query = "SELECT ca.clothing_name, ca.size, cn.clothing_price FROM \"Clothing/Accessory item\" ca JOIN \"Clothing/Accessory item name\" cn ON ca.clothing_name = cn.clothing_name WHERE ca.clothing_RefNb = %s;"
        cursor.execute(query, (itemRefNo,))
        row = cursor.fetchone()

        if row:
            item = [
                 itemRefNo,
                 row[0],
                 row[1],
                 row[2],
                 1
            ]

            for item in cart:
                if item[0]==itemRefNo:
                    item[4]+=1
                    return redirect('/cart')
            
            cart.append(item)
            

            return redirect('/cart')

# View cart
@app.route('/cart')
def view_cart():
    total = sum(item[3] * item[4] for item in cart)
    return render_template('cart.html',cart=cart ,total=total)

# Remove item from cart
@app.route('/cart/removefromcart/<int:product_id>',methods=['POST','GET'])
def remove_from_cart(product_id):
    for item in cart:
        if item[0]==product_id:
            cart.remove(item)
            break

    return render_template('cart.html')


      ####################### cosmetics ads
    cursor.execute('select distinct on ("cosmetic_name") "cosmetic_name","cosmetic_price","cosmetic_discount","cosmetic_description","cosmetic_photos","Cosmetic item"."cosmetic_RefNb" from "Cosmetic item","Photos Cosmetic" where "Cosmetic item"."cosmetic_RefNb"="Photos Cosmetic"."cosmetic_RefNb" limit 8')
    cosmetics_ad=cursor.fetchall()
    for i in range(len(cosmetics_ad)):
        cosmetics_ad[i]=list(cosmetics_ad[i])
        cosmetics_ad[i][1]=round(cosmetics_ad[i][1],2)
        cosmetics_ad[i].append(round(cosmetics_ad[i][1]/(1-cosmetics_ad[i][2]),2))
        cosmetics_ad[i][2]=cosmetics_ad[i][2]*100
    return render_template("main.html",discounted_items=discounted_items,
                           best_sellers=best_sellers,
                           search_results_cloth=search_results_cloth,search_results_cos=search_results_cos,search=search,cosmetics_ad=cosmetics_ad)


def user_exists(email):
    cursor = conn.cursor()
    query = 'SELECT * FROM "Customer" WHERE "customer_email" = %s'
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    return user is not None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        address = request.form['address']
        phone_number = request.form['phone_number']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
        credit_card = request.form['credit_card']
        password = request.form['password']

        if user_exists(email):
            flash('User already exists. Please log in.')
            return redirect('/login')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO "Customer" ("customer_email","FName","LName", "gender", "address", "phonenumber", "DOB", "credit card","password")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, (email, first_name, last_name, gender, address, phone_number, date_of_birth, credit_card,password))

        conn.commit()

        flash('Signup successful! Please login.')
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute('SELECT "password" FROM "Customer" WHERE "customer_email" = %s', (email,))
        conn.commit()
        user = cursor.fetchone()
        print(user)

        if password in user:  
            flash('Login successful!')
            user_logged_in = True
            session['user_logged_in'] = user_logged_in
            session['user_id'] = email
            return redirect("/")
        else:
            flash('Invalid email or password. Please try again.')

    return render_template('login.html')


if __name__ == "__main__":
    app.run()
