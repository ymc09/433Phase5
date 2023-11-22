@app.route('/cart/removefromcart/<int:product_id>',methods=['POST','GET'])
def remove_from_cart(product_id):
    for item in cart:
        if item[0]==product_id:
            cart.remove(item)
            break
        
    return redirect('/cart')
