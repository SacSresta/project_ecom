from store.models import Product,Profile,ProductVariant
from decimal import Decimal

class Cart():
    def __init__(self,request) -> None:
        self.session = request.session
        #Get request
        self.request = request
        
        #Get the current session key if it exists
        cart = self.session.get('session_key')
        
        #If the user is new, no session! Create one!
        if 'session_key' not in request.session:
            cart =self.session['session_key'] = {}
            
        #Make sure cart is available on all the pages of site
        self.cart = cart
        

    def db_add(self,product,quantity,size):
        product_id = str(product)
        global product_qty
        product_qty = int(quantity)  # Convert to integer for comparison
        product_size = size

        # Ensure product_qty is greater than 0
        if product_qty > 0:
            # Logic
            if product_id in self.cart:
                pass  # You can add any logic here if needed when the product is already in the cart
            else:
                self.cart[product_id] = {str(product_qty):product_size}

            self.session.modified = True

            # Deal with the logged-in user
            if self.request.user.is_authenticated:
                # Get the current user Profile
                current_user = Profile.objects.filter(user__id=self.request.user.id)
                # Convert cart dictionary to a JSON string
                carty = str(self.cart)
                carty = carty.replace("'", "\"")
                # Save carty to Profile Model
                current_user.update(old_cart=str(carty))
        else:
            # Handle the case where quantity is 0 or less (optional)
            # You could remove the item from the cart or raise an error
            pass 
    def add(self, product, quantity,size):
        product_id = str(product.id)
        global product_qty
        product_qty = int(quantity)  # Convert to integer for comparison
        product_size = size

        # Ensure product_qty is greater than 0
        if product_qty > 0:
            # Logic
            if product_id in self.cart:
                pass  # You can add any logic here if needed when the product is already in the cart
            else:
                self.cart[product_id] = {str(product_qty):str(product_size)}

            self.session.modified = True

            # Deal with the logged-in user
            if self.request.user.is_authenticated:
                # Get the current user Profile
                current_user = Profile.objects.filter(user__id=self.request.user.id)
                # Convert cart dictionary to a JSON string
                carty = str(self.cart)
                carty = carty.replace("'", "\"")
                # Save carty to Profile Model
                current_user.update(old_cart=str(carty))
        else:
            # Handle the case where quantity is 0 or less (optional)
            # You could remove the item from the cart or raise an error
            pass
    
    
    def cart_total(self):
        total = Decimal(0)  # Initialize total as a Decimal to match the product price types
        products = Product.objects.filter(id__in=self.cart.keys())
        variants = ProductVariant.objects.filter(id__in=self.cart.keys())
        variant = [v.product for v in variants]
        
        for key, value in self.cart.items():
            key = int(key)  # Convert key to int to match product ID
            qty_value = next(iter(value.keys()))  # Assuming you want to use the first key from the dict
            qty_value = Decimal(qty_value)  # Convert quantity to Decimal
            #print(qty_value)
            for variant in variants:
                if variant.id == key:
                    if variant.product.is_sale:
                        total += variant.product.sale_price * qty_value
                    else:
                        total += variant.product.price * qty_value

        return total
    
    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        
        # Use ids to look up products in the database model
        variant = ProductVariant.objects.filter(id__in=product_ids)        
        # Return the looked up products
        return variant
    
    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self,product,quantity,size):
        product_id = str(product)
        product_qty = int(quantity)
        product_size = int(size)        
        #Get Cart
        ourcart = self.cart
        ourcart[product_id] = {product_qty:int(product_size)}
        
        self.session.modified = True
        
        thing = self.cart
        
        if self.request.user.is_authenticated:
            #Get the current user Profile
            
            current_user = Profile.objects.filter(user__id = self.request.user.id)
            #{'3':1,'2':4} to{"3":1,"2":4} 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            #Save carty to Profile Model
            current_user.update(old_cart = str(carty))    
        
        return thing
    def delete(self,product):
        product_id = str(product)
        
        #delete from dictionary/cart
        
        if product_id in self.cart:
            del self.cart[product_id]
        
        
        self.session.modified = True
             
        if self.request.user.is_authenticated:
            #Get the current user Profile
            
            current_user = Profile.objects.filter(user__id = self.request.user.id)
            #{'3':1,'2':4} to{"3":1,"2":4} 
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            #Save carty to Profile Model
            current_user.update(old_cart = str(carty))    
            
        
        
    def get_size(self):
        product_id_list = self.cart.keys()
        sizes = [int(list(i.values())[0]) for i in self.cart.values()]
        return sizes
        
    
    def get_size_variation(self):
        product_id_list = self.cart.keys()
        products = Product.objects.filter(id__in=product_id_list)
        sizes = {product.id: [int(variant.size) for variant in product.variants.all()] for product in products}
        return sizes
        
    def new_total(self):
        total = Decimal(self.session.get('total', '0'))  # Convert the string back to Decimal
        return total
    
        
        
        '''print(size)
            for product_id in product_id_list:
                product = Product.objects.get(id=product_id)
                product_variant = product.variants.all()
                product_variant.get'''
            
