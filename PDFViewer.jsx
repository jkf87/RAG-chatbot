import React, { useState } from 'react';
import { Document, Page } from 'react-pdf';
import { Streamlit } from "streamlit-component-lib";

function PDFViewer({ pdfBase64, initialPage }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(initialPage);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    Streamlit.setFrameHeight();
  }

  function changePage(offset) {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      Streamlit.setComponentValue(newPageNumber);
      return newPageNumber;
    });
  }

  return (
    <div>
      <Document
        file={`data:application/pdf;base64,${pdfBase64}`}
        onLoadSuccess={onDocumentLoadSuccess}
      >
        <Page pageNumber={pageNumber} />
      </Document>
      <p>
        Page {pageNumber} of {numPages}
      </p>
      <button disabled={pageNumber <= 1} onClick={() => changePage(-1)}>
        Previous
      </button>
      <button
        disabled={pageNumber >= numPages}
        onClick={() => changePage(1)}
      >
        Next
      </button>
    </div>
  );
}

export default PDFViewer;