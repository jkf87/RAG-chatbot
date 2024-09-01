import React from 'react'
import ReactDOM from 'react-dom'
import PDFViewer from './PDFViewer'
import { StreamlitProvider } from "streamlit-component-lib"

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
      <PDFViewer />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById('root')
)
