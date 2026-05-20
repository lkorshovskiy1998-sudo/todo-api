from flask import Flask, jsonify, request

app = Flask(__name__)

products = [
    {"id": 1, "name": "iPhone", "price": 1000},
    {"id": 2, "name": "Samsung", "price": 800}
]

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

@app.route("/products", methods=["POST"])
def add_products():
    data = request.json

    products.append(data)

    return jsonify({
        "message": "Товар додано",
        "products": data
    })

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    for p in products:
        if p['id'] == product_id:
            products.remove(p)
            return jsonify({
                "message": "Товар видалено"
            }), 200
    return jsonify({
        "message": "Товар не знайдено"
    }), 404

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json

    for p in products:
        if p['id'] == product_id:
            p['name'] = data['name']
            p['price'] = data['price']
            return jsonify({
                "message": "Товар оновлено", 
                "product": p
            })
    
    return jsonify({
        "message": "Товар не знайдено"
    })

app.run(debug=True)