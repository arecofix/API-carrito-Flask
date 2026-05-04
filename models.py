from extensions import db

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {"id": self.id, "servicio": self.servicio, "precio": self.precio}

class CartItem(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    
    service = db.relationship('Service')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="COMPLETED")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    service = db.relationship('Service')
