# Vendor Store – Full Request Bodies

One API: **PUT /vendor/vendor-stores/** for store + **cover_photos** / **cover_videos** (multiple files in same request). Raw body = JSON (no files); media = multipart/form-data (store fields + profile_image, banner_image, cover_photos, cover_videos).

---

## 1. Vendor Store (GET / PUT)

**Endpoint:** `PUT /vendor/vendor-stores/`  
**Auth:** Required (logged-in vendor). Same API accepts store fields **and** cover photos/videos (multiple files).

---

### 1.1 Raw body (application/json)

Use when sending only text/numbers (no images). Omit file fields or send `null`.

```json
{
  "name": "My Fashion Store",
  "about": "Best ethnic and western wear in the city.",
  "business_type": "Retail",
  "store_mobile": "9876543210",
  "store_email": "store@example.com",
  "house_building_no": "Block A, Shop 12",
  "locality_street": "MG Road",
  "pincode": "400001",
  "state": "Maharashtra",
  "city": "Mumbai",
  "owner_gender": "male",
  "vendor_house_no": "101",
  "vendor_locality_street": "Park Street",
  "vendor_pincode": "400002",
  "vendor_state": "Maharashtra",
  "vendor_city": "Mumbai",
  "storetag": "fashion",
  "latitude": "19.076090",
  "longitude": "72.877426",
  "is_location": true,
  "is_active": true,
  "is_online": true
}
```

**Field list (all writable store fields):**

| Field | Type | Example |
|-------|------|---------|
| `name` | string | "My Fashion Store" |
| `about` | string (max 500) | "Best ethnic and western wear." |
| `business_type` | string | "Retail" |
| `profile_image` | (file – use multipart) | — |
| `banner_image` | (file – use multipart) | — |
| `store_mobile` | string | "9876543210" |
| `store_email` | string (email) | "store@example.com" |
| `house_building_no` | string | "Block A, Shop 12" |
| `locality_street` | string | "MG Road" |
| `pincode` | string | "400001" |
| `state` | string | "Maharashtra" |
| `city` | string | "Mumbai" |
| `owner_gender` | string | "male" \| "female" \| "other" |
| `vendor_house_no` | string | "101" |
| `vendor_locality_street` | string | "Park Street" |
| `vendor_pincode` | string | "400002" |
| `vendor_state` | string | "Maharashtra" |
| `vendor_city` | string | "Mumbai" |
| `storetag` | string | "fashion" |
| `latitude` | decimal string | "19.076090" |
| `longitude` | decimal string | "72.877426" |
| `is_location` | boolean | true |
| `is_active` | boolean | true |
| `is_online` | boolean | true |

---

### 1.2 Media agent body (multipart/form-data)

Use when uploading **profile_image**, **banner_image**, and/or **cover_photos** / **cover_videos**. All in the same PUT.

**Content-Type:** `multipart/form-data`

**Form fields (same as raw body) + file keys:**

| Key | Type | Description |
|-----|------|-------------|
| `name` | text | Store name |
| `about` | text | Store description |
| `business_type` | text | Business type |
| `profile_image` | **file** | Store logo (image) |
| `banner_image` | **file** | Store banner (image) |
| `cover_photos` or `cover_photos[]` | **file (multiple)** | Cover photos – send one key per file or multiple files under same key; replaces existing cover photos |
| `cover_videos` or `cover_videos[]` | **file (multiple)** | Cover videos – same as above; replaces existing cover videos |
| `store_mobile` | text | Store mobile |
| `store_email` | text | Store email |
| `house_building_no` | text | House/Building no. |
| `locality_street` | text | Locality/Street |
| `pincode` | text | Pincode |
| `state` | text | State |
| `city` | text | City |
| `owner_gender` | text | male / female / other |
| `vendor_house_no` | text | Owner house no. |
| `vendor_locality_street` | text | Owner locality |
| `vendor_pincode` | text | Owner pincode |
| `vendor_state` | text | Owner state |
| `vendor_city` | text | Owner city |
| `storetag` | text | Store tag |
| `latitude` | text | Latitude |
| `longitude` | text | Longitude |
| `is_location` | text | "true" / "false" |
| `is_active` | text | "true" / "false" |
| `is_online` | text | "true" / "false" |

**Example (multipart):**

```
------WebKitFormBoundary
Content-Disposition: form-data; name="name"

My Fashion Store
------WebKitFormBoundary
Content-Disposition: form-data; name="about"

Best ethnic and western wear in the city.
------WebKitFormBoundary
Content-Disposition: form-data; name="business_type"

Retail
------WebKitFormBoundary
Content-Disposition: form-data; name="profile_image"; filename="logo.png"
Content-Type: image/png

(binary)
------WebKitFormBoundary
Content-Disposition: form-data; name="banner_image"; filename="banner.jpg"
Content-Type: image/jpeg

(binary)
------WebKitFormBoundary
Content-Disposition: form-data; name="store_mobile"

9876543210
------WebKitFormBoundary
Content-Disposition: form-data; name="store_email"

store@example.com
------WebKitFormBoundary
Content-Disposition: form-data; name="house_building_no"

Block A, Shop 12
------WebKitFormBoundary
Content-Disposition: form-data; name="locality_street"

MG Road
------WebKitFormBoundary
Content-Disposition: form-data; name="pincode"

400001
------WebKitFormBoundary
Content-Disposition: form-data; name="state"

Maharashtra
------WebKitFormBoundary
Content-Disposition: form-data; name="city"

Mumbai
------WebKitFormBoundary
Content-Disposition: form-data; name="owner_gender"

male
------WebKitFormBoundary
Content-Disposition: form-data; name="vendor_house_no"

101
------WebKitFormBoundary
Content-Disposition: form-data; name="vendor_locality_street"

Park Street
------WebKitFormBoundary
Content-Disposition: form-data; name="vendor_pincode"

400002
------WebKitFormBoundary
Content-Disposition: form-data; name="vendor_state"

Maharashtra
------WebKitFormBoundary
Content-Disposition: form-data; name="vendor_city"

Mumbai
------WebKitFormBoundary
Content-Disposition: form-data; name="storetag"

fashion
------WebKitFormBoundary
Content-Disposition: form-data; name="latitude"

19.076090
------WebKitFormBoundary
Content-Disposition: form-data; name="longitude"

72.877426
------WebKitFormBoundary
Content-Disposition: form-data; name="is_location"

true
------WebKitFormBoundary
Content-Disposition: form-data; name="is_active"

true
------WebKitFormBoundary
Content-Disposition: form-data; name="is_online"

true
------WebKitFormBoundary--
```

---

## 2. Response (Vendor Store GET)

**Read-only fields** (returned by API, not sent in request):

- `id`, `user`
- `vendor_name` (from user first_name + last_name)
- `cover_photos` (list of cover media with `media_type=image`)
- `cover_videos` (list of cover media with `media_type=video`)
- `cover_photos_videos` (combined list)
- `reels`, `banners`
- `store_rating`, `reviews`

Each cover item in response:

```json
{
  "id": 1,
  "media_type": "image",
  "media": "/media/store/cover_media/cover1.jpg",
  "media_url": "https://your-domain.com/media/store/cover_media/cover1.jpg",
  "order": 0,
  "created_at": "2026-01-29T12:00:00Z"
}
```
