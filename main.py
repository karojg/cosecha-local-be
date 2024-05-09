from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pdfplumber
from io import BytesIO
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, firestore
from helpers import read_csv_as_dict

app = FastAPI()

# Firebase initialization
cred = credentials.Certificate(
    "service_accounts/cosecha-local-419502-firebase-adminsdk-yawzl-93e7339330.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()


class Product(BaseModel):
    id: int
    semana: int
    product: str
    type: str
    size: str
    unit: str
    price: int


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int) -> Optional[Product]:
    data = read_csv_as_dict()
    for item in data:
        if item.get("id") == product_id:
            return Product(**item)
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/")
def get_all_products() -> List[Product]:
    return read_csv_as_dict()


@app.get("/download-extract-and-store/")
async def extract_pdf_text():
    file_name = "PS_PAI_Semana_19-03_al_09-05-2024"
    week = "19-04"
    date = "09-05-2024"

    pdf_url = f"https://www.cnp.go.cr/pai/precios%20de%20compra/2024/{file_name}.pdf"

    # Send a GET request to download the PDF
    response = requests.get(pdf_url)
    response.raise_for_status()  # Ensure the request was successful

    # Load the PDF from the in-memory bytes buffer
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables(
                {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "explicit_vertical_lines": page.curves + page.edges,
                    "explicit_horizontal_lines": page.curves + page.edges,
                    "snap_tolerance": 3,
                    "join_tolerance": 3,
                }
            )

            for table in page_tables:
                headers = table[0]
                # excludes header info
                rows = table[3:]
                # Correct headers if they are misaligned or missing
                expected_headers = [
                    "Código",
                    "Productos",
                    "Tipo",
                    "Calidad/Tamaño",
                    "Unidad de Venta",
                    "Precio compra",
                ]
                if headers != expected_headers:
                    # Create a mapping between expected headers and desired renamed headers
                    header_mapping = {
                        "Código": "id",
                        "Productos": "name",
                        "Tipo": "type",
                        "Calidad/Tamaño": "quality",
                        "Unidad de Venta": "unit",
                        "Precio compra": "price",
                    }
                    # Rename headers using the mapping
                    headers = [header_mapping.get(header, header) for header in expected_headers]

                corrected_rows = [
                    dict(zip(headers, row)) for row in rows if len(row) == len(headers)
                ]

        try:
            store_pdf_data(corrected_rows, week)
        except Exception as e:
            return {"status": f"Error extracting data: {e}"}
        
    return {"status": "Data extracted and stored in Firestore"}


def store_pdf_data(json_data, week_number):
    for obj in json_data:
        # Specify custom document ID
        doc_id = obj["id"]  # Assuming your data contains an "id" field for custom IDs
        # Add the object as a document to Firestore with custom ID
        product_ref = db.collection('your_collection_nested').document(doc_id)
        week_ref = product_ref.collection('weeks').document(week_number)
        week_ref.set(obj)

        print(f'Data uploaded for product {doc_id}, week {week_number}')
