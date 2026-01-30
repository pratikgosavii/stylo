# API Reference for Frontend Developer

Base URL: `https://your-domain.com` (replace with your actual backend URL)

**Authentication:** All customer and vendor APIs require authentication. Send the JWT token in the header:
```
Authorization: Bearer <access_token>
```

---

## 1. List Products (Customer)

**GET** `/customer/list-products/`

Returns active products (filtered by customer's city/pincode when applicable).

| Item | Value |
|------|--------|
| **Permission** | Authenticated |
| **Query params** | Optional filters (e.g. category, search) via `ProductFilter` |

**Response:** List of product objects (id, name, category, sales_price, image, etc.).

**Example:**
```http
GET /customer/list-products/
Authorization: Bearer <access_token>
```

---

## 2. Add to Cart (Customer)

**POST** `/customer/cart/`

Add a product to the current user's cart. If the product is already in the cart, quantity is increased.

| Item | Value |
|------|--------|
| **Permission** | Authenticated |
| **Content-Type** | `application/json` |

**Request body:**
```json
{
  "product": 1,
  "quantity": 2
}
```
- `product` (required): Product ID (integer).
- `quantity` (optional): Default `1`.

**Response:** Created/updated cart item with `id`, `product`, `quantity`, `product_details`.

**Example:**
```http
POST /customer/cart/
Authorization: Bearer <access_token>
Content-Type: application/json

{"product": 5, "quantity": 2}
```

---

## 3. List Cart (Customer)

**GET** `/customer/cart/`

Returns the current user's cart items.

**Response:** List of cart items, each with `id`, `product`, `quantity`, `product_details`.

---

## 4. Clear Cart (Customer)

**POST** `/customer/cart/clear_cart/`

Removes all items from the current user's cart.

| Item | Value |
|------|--------|
| **Permission** | Authenticated |

**Request body:** Empty or `{}`.

**Response:**
```json
{
  "message": "Cart cleared successfully ✅"
}
```

**Example:**
```http
POST /customer/cart/clear_cart/
Authorization: Bearer <access_token>
Content-Type: application/json

{}
```

---

## 5. Update Cart Item Quantity (Customer)

**PATCH** `/customer/cart/<cart_item_id>/update_quantity/`

Update the quantity of a single cart item.

**Request body:**
```json
{
  "quantity": 3
}
```
If `quantity` is 0 or less, the item is removed from the cart.

---

## 6. Clear Cart and Add One Product (Customer)

**POST** `/customer/cart/clear_and_add/`

Clears the entire cart and adds one product (e.g. for “buy now” flow).

**Request body:**
```json
{
  "product": 10,
  "quantity": 1
}
```

**Response:** The new cart item (single item in cart).

---

## 7. Add Address (Customer)

**POST** `/customer/address/`

Create a new address for the current user.

| Item | Value |
|------|--------|
| **Permission** | Authenticated |
| **Content-Type** | `application/json` |

**Request body:**
```json
{
  "full_name": "John Doe",
  "mobile_number": "9876543210",
  "city": "Mumbai",
  "flat_building": "Building A, Flat 101",
  "area_street": "Main Street",
  "landmark": "Near Park",
  "state": "Maharashtra",
  "latitude": "19.0760",
  "longitude": "72.8777",
  "is_default": true,
  "delivery_instructions": "Ring the bell"
}
```
- `user` is set automatically from the token; do not send it.
- `state` must be one of the Indian states (e.g. "Maharashtra", "Karnataka").
- `latitude`, `longitude`: decimals as strings or numbers.

**Response:** Created address object with all fields.

**Example:**
```http
POST /customer/address/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "mobile_number": "9123456789",
  "city": "Pune",
  "flat_building": "Tower B",
  "area_street": "MG Road",
  "state": "Maharashtra",
  "latitude": "18.5204",
  "longitude": "73.8567",
  "is_default": true
}
```

---

## 8. List Addresses (Customer)

**GET** `/customer/address/`

Returns all addresses for the current user.

---

## 9. Update / Delete Address (Customer)

- **PUT** `/customer/address/<id>/` – Full update.
- **PATCH** `/customer/address/<id>/` – Partial update.
- **DELETE** `/customer/address/<id>/` – Delete address.

---

## 10. Add New Product (Vendor)

**POST** `/vendor/product/`

Create a new product. **Vendor role only.**

| Item | Value |
|------|--------|
| **Permission** | Vendor (IsVendor) |
| **Content-Type** | `multipart/form-data` or `application/json` (for non-file fields) |

**Request body:** Product fields as per `product` model, e.g.:
- `name`, `category`, `sub_category`, `sales_price`, `mrp`, `purchase_price`, `wholesale_price`
- `serial_numbers`, `stock`, `opening_stock`
- `description`, `image`, `brand_name`, `color`, `size`, `batch_number`, `expiry_date`
- `replacement`, `shop_exchange`, `shop_warranty`, `brand_warranty`
- `tax_inclusive`, `is_popular`, `is_featured`, `is_active`
- `gst`, `hsn`, etc.

`user` is set automatically from the logged-in vendor; do not send it.

**Response:** Created product object.

**Example (minimal JSON):**
```http
POST /vendor/product/
Authorization: Bearer <vendor_access_token>
Content-Type: application/json

{
  "name": "New Product",
  "category": 1,
  "sub_category": 1,
  "sales_price": "299.00",
  "mrp": "399.00",
  "serial_numbers": 100,
  "stock": 100,
  "description": "Product description",
  "is_active": true
}
```
For image upload, use `multipart/form-data` and send `image` as a file.

---

## 11. List / Update / Delete Product (Vendor)

- **GET** `/vendor/product/` – List current vendor's products.
- **GET** `/vendor/product/<id>/` – Product detail.
- **PUT** `/vendor/product/<id>/` – Full update.
- **PATCH** `/vendor/product/<id>/` – Partial update.
- **DELETE** `/vendor/product/<id>/` – Delete product.

---

## Quick reference table

| Feature           | Method | Endpoint |
|-------------------|--------|----------|
| List products     | GET    | `/customer/list-products/` |
| Add to cart       | POST   | `/customer/cart/` |
| List cart         | GET    | `/customer/cart/` |
| Clear cart        | POST   | `/customer/cart/clear_cart/` |
| Update cart qty   | PATCH  | `/customer/cart/<id>/update_quantity/` |
| Clear & add one   | POST   | `/customer/cart/clear_and_add/` |
| Add address       | POST   | `/customer/address/` |
| List addresses    | GET    | `/customer/address/` |
| Update address    | PUT/PATCH | `/customer/address/<id>/` |
| Delete address    | DELETE | `/customer/address/<id>/` |
| Add product (vendor) | POST | `/vendor/product/` |
| List products (vendor) | GET | `/vendor/product/` |
| Product detail (vendor) | GET | `/vendor/product/<id>/` |
| Update product (vendor) | PUT/PATCH | `/vendor/product/<id>/` |
| Delete product (vendor) | DELETE | `/vendor/product/<id>/` |

---

## Authentication

Obtain access token via your login API (e.g. JWT). Use it in every request:

```
Authorization: Bearer <access_token>
```

Customer endpoints require a **customer** user; product create/update/delete require a **vendor** user.
