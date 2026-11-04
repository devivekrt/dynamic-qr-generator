# QRevive

> Change the content, not the code.

**Use the live site:** [Open QR Code Generator](https://appsail-50047107962.development.catalystappsail.in)

A business can create multiple permanent QR codes. Customers scan a QRevive QR code
and open its current destination directly. The owner can update text, links,
images, or PDFs without printing a new QR code.

The application is hosted with [Zoho Catalyst](https://www.zoho.com/catalyst/).

## How to use

1. Open the [live site](https://appsail-50047107962.development.catalystappsail.in).
2. Create an account and log in.
3. Create a QR code, then choose **Set destination**.
4. Choose a link, text, image, or PDF and save it.
5. Download and print the QR code.
6. Later, use **Update destination**, **Edit text**, **Edit link**, or
   **Replace file**. The printed QR code continues to work.

## QR code behavior

- Each QR code has one permanent destination.
- Link QR codes open the current link.
- Text QR codes display the current text.
- Image and PDF QR codes open the current file.
- Updating the destination does not change the QR code.
- QR designs are plan-controlled: Free accounts can use basic patterns, Prime
  accounts can use designed templates and custom colors, and Business accounts
  can use advanced templates and logos.

## Developer information

The frontend uses React and Vite. The backend uses Python, FastAPI, Catalyst
Data Store, and Catalyst File Store. Local development instructions are
provided for contributors.

### Run locally

```bash
cd client
npm install
npm run build
```

The build outputs directly to `functions/api/client`, which is the static
frontend directory served by AppSail. Then run the backend:

```bash
cd functions/api
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Documentation

- [Architecture](docs/architecture.md)
- [API documentation](docs/api-documentation.md)
- [Catalyst data schema](database/schema.md)
