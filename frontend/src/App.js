import React, { useState, useEffect } from "react";
import styled from "styled-components";
import axios from "axios";
import {
  AppBar,
  Toolbar,
  Typography,
  Container as MuiContainer, // Rename Container to avoid conflict
  TextField,
  Button,
  CircularProgress,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox, 
  FormControlLabel
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import SendIcon from "@mui/icons-material/Send";
import PostAddIcon from "@mui/icons-material/PostAdd";
import FileUploadIcon from "@mui/icons-material/FileUpload";
import RefreshIcon from "@mui/icons-material/Refresh";
import Tooltip from "@mui/material/Tooltip";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import "./styles.css";
// import cloudinary from 'cloudinary';

// const StyledNavbar = styled(Navbar)`
//   background-color: #1976d2; /* Primary color */
//   color: #fff; /* Text color */
// `;

// const StyledNavbarBrand = styled(Navbar.Brand)`
//   font-size: 24px;
//   font-weight: bold;
//   margin-right: 50px; /* Adjust as needed */
// `;

const ContactCard = ({ doctor }) => {
  const { Name, Location, "Phone Number": phoneNumber } = doctor;

  return (
    <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
      <h2>{Name}</h2>
      <p>Location: {Location}</p>
      <p>Phone Number: {phoneNumber}</p>
    </div>
  );
};

const ContactList = ({ doctors }) => {
  return (
    <div>
      <h1>Top Doctors</h1>
      {doctors && doctors.map((doctor, index) => (
        <ContactCard key={index} doctor={doctor} />
      ))}
    </div>
  );
};

const MedicalChatbot = () => {
  const [query, setQuery] = useState("");
  const [doc, setFile] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [queryInProgress, setQueryInProgress] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [isPrescription, setIsPrescription] = useState(true);
  const [count, setCount] = useState(0);
  // const [topdoctors,setDoctors] = useState([]);
  let topdoctors;
  const handleQuestionChange = (event) => {
    setQuery(event.target.value);
  };

  const handlePrescriptionSubmit = () => {
    setOpenModal(true);
  };

  const handleCloseModal = () => {
    setOpenModal(false);
  };

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    await setFile(selectedFile);
  };

  const handleUploadSubmit = async () => {
    try {
      if (!doc) {
        console.error("No file selected");
        return;
      }

      const formData = new FormData();
      formData.append("file", doc);

      const totalSize = doc.size;

      const response = await axios.post(
        "http://localhost:8000/uploadpdf",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      alert("File successfully uploaded!");
      // Handle the response if needed
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error occurred while uploading file");
    }
  };

  const getDoctorMapping = () => {
    const doctors = [
      {
        'Name': 'Dr. Ayan Dey',
        'Location': 'Kolkata',
        'Phone Number': '+91 98765 43210',
        'Similarity': 0.85
      },
      {
        'Name': 'Dr. Arpita Ghosh',
        'Location': 'Kolkata',
        'Phone Number': '+91 87654 32109',
        'Similarity': 0.73
      },
      {
        'Name': 'Dr. Priyanka Das',
        'Location': 'Kolkata',
        'Phone Number': '+91 76543 21098',
        'Similarity': 0.62
      },
      {
        'Name': 'Dr. Souvik Bose',
        'Location': 'Kolkata',
        'Phone Number': '+91 65432 10987',
        'Similarity': 0.77
      },
      {
        'Name': 'Dr. Ananya Sen',
        'Location': 'Kolkata',
        'Phone Number': '+91 54321 09876',
        'Similarity': 0.48
      },
      {
        'Name': 'Dr. Riddhi Majumdar',
        'Location': 'Kolkata',
        'Phone Number': '+91 43210 98765',
        'Similarity': 0.55
      },
      {
        'Name': 'Dr. Suman Ghosh',
        'Location': 'Kolkata',
        'Phone Number': '+91 32109 87654',
        'Similarity': 0.82
      },
      {
        'Name': 'Dr. Ishita Dasgupta',
        'Location': 'Kolkata',
        'Phone Number': '+91 21098 76543',
        'Similarity': 0.67
      },
      {
        'Name': 'Dr. Abhishek Chatterjee',
        'Location': 'Kolkata',
        'Phone Number': '+91 10987 65432',
        'Similarity': 0.58
      },
      {
        'Name': 'Dr. Rupa Basu',
        'Location': 'Kolkata',
        'Phone Number': '+91 09876 54321',
        'Similarity': 0.75
      }
    ];
    if(count %3  === 0) {
      const evenIndexDoctors = doctors.filter((doctor, index) => index % 2 === 0);
      evenIndexDoctors.sort((a, b) => b.Similarity - a.Similarity);
      const top3Doctors = evenIndexDoctors.slice(0, 3);
      console.log(top3Doctors);
      // setDoctors(top3Doctors);
      topdoctors = top3Doctors;
    }
    else if(count%3 === 1) {
      const evenIndexDoctors = doctors.filter((doctor, index) => index % 3 === 0);
      evenIndexDoctors.sort((a, b) => b.Similarity - a.Similarity);
      const top3Doctors = evenIndexDoctors.slice(0, 3);
      console.log(top3Doctors);
      topdoctors = top3Doctors;
    }
    else if(count%3 === 2) {
      doctors.sort((a, b) => b.Similarity - a.Similarity);
      const top3Doctors = doctors.slice(0, 3);
      console.log(top3Doctors);
      topdoctors = top3Doctors;
    }
    setCount(count + 1);
    console.log(topdoctors);
  }

  const handleFileUpload = async (event) => {
    console.log("Entering the handleFile");
    const file = event.target.files[0];

    try {
      const formData = new FormData();
      formData.append("file", file);
    
      const response = await axios.post(
        "http://localhost:8000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
    
      console.log(response);
      const secure_url = response.data.file_url.secure_url; // Adjust this line
      console.log("Now moving to the parse-prescription");
      console.log(secure_url)
      let response2
      if(isPrescription) {
        response2 = await axios.post(
          "http://localhost:8080/parse-prescription",
          {
            "url": secure_url,
            "isPrescription": true
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
      }
      else {
        response2 = await axios.post(
          "http://localhost:8080/parse-report",
          {
            "url": secure_url,
            "isPrescription": true
          },
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
      }
      
      console.log(response2.data)

      const response3 = await fetch(
        `http://localhost:8000/search/?query=${encodeURIComponent(response2.data + "These are my medications. Use these as context.")}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const data_fetched = await response3.json();
      console.log(data_fetched);

      // if (!response2.ok) { // Adjust this line
      //   throw new Error(`Failed to parse prescription: ${response2.statusText}`); // Adjust this line
      // }
    
      console.log("Prescription parsed successfully");
      handleCloseModal();
    } catch (error) {
      console.error("Error:", error);
    }
  }

  // const handleFileUpload = async (event) => {
  //   const file = event.target.files[0];

  //   try {
  //     // Configure Cloudinary with your cloud name, API key, and API secret
  //     cloudinary.config({
  //       cloud_name: 'dqln5phax',
  //       api_key: '373247933775311',
  //       api_secret: 'waEbZ9xlEpjAp8PhMfP6ESw3ZCs'
  //     });

  //     // Upload the file to Cloudinary
  //     const result = await cloudinary.v2.uploader.upload(file, {
  //       folder: 'your_folder', // Optional: specify a folder in Cloudinary
  //       resource_type: 'auto' // Automatically detect the resource type
  //     });

  //     // Log the URL of the uploaded file
  //     console.log('File uploaded successfully:', result.secure_url);

  //     // Close the modal or perform any other action
  //     handleCloseModal();
  //   } catch (error) {
  //     console.error('Error uploading file to Cloudinary:', error);
  //   }
  // };

  // const handleFileUpload = async (event) => {
  //   const file = event.target.files[0];

  //   try {
  //     const options = {
  //       types: [
  //         {
  //           description: "PDF Files",
  //           accept: {
  //             "application/pdf": [".pdf"],
  //           },
  //         },
  //       ],
  //       suggestedName: "P1.pdf", // Set the suggested filename
  //     };

  //     const handle = await window.showSaveFilePicker(options);
  //     const writable = await handle.createWritable();
  //     await writable.write(file);
  //     await writable.close();

  //     console.log("File saved successfully:", file.name);
  //     handleCloseModal();
  //   } catch (error) {
  //     console.error("Error saving file:", error);
  //   }
  // };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    setQueryInProgress(true);
    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/search/?query=${encodeURIComponent(query)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      console.log(response);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      const newMessage = {
        query: query,
        answer: data.response,
      };

      setConversationHistory((prevHistory) => [...prevHistory, newMessage]);
      setQueryInProgress(false);
      getDoctorMapping();
    } catch (error) {
      console.error("Error:", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      // Reload the page
      window.location.reload();

      // Send a request to restart the Django backend
      await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (error) {
      console.error("Error refreshing page and restarting server:", error);
    }
  };

  return (
    <div
      style={{
        backgroundColor: "#f7f7f7",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        zIndex: 1105,
      }}
    >
      <div
        style={{
          backgroundColor: "#8db3f0",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 14px",
        }}
      >
        <Navbar bg="primary" data-bs-theme="dark">
          <Container>
            <Navbar.Brand>MediBuddy</Navbar.Brand>
            {/* <Nav className="me-auto">
            <Nav.Link href="#home">Home</Nav.Link>
            <Nav.Link href="#features">Features</Nav.Link>
            <Nav.Link href="#pricing">Pricing</Nav.Link>
          </Nav> */}
          </Container>
        </Navbar>
        {/* <h3 style={{ margin: 0 }}>MediBuddy</h3> */}
        <Button
          onClick={handleRefresh}
          style={{
            textTransform: "none",
            display: "flex",
            alignItems: "center",
          }}
        >
          <AddIcon />
          <Typography variant="body1" style={{ marginLeft: "6px" }}>
            NEW CHAT
          </Typography>
        </Button>
      </div>

      <div style={{ overflow: "auto", flex: "1" }}>
        {conversationHistory.map((message, indx) => (
          <div key={indx} style={{ marginBottom: "2px", userSelect: "text" }}>
            <div style={{ margin: "0" }}>
              {/* <p style={{ fontWeight: 'bold', margin: '10px' }}>Question:</p> */}
              <p
                style={{
                  backgroundColor: "#cad8e6",
                  borderRadius: "10px",
                  // border: '1px solid black',
                  padding: "10px",
                  margin: "10px",
                  marginLeft: "20px",
                  marginBottom: "15px",
                  alignSelf: "flex-start",
                  maxWidth: "70%",
                  // display: 'inline-block',
                  // userSelect: 'text', // Make the text selectable
                }}
              >
                {message.query}
              </p>
            </div>

            <div
              style={{
                paddingBottom: "5px",
                marginLeft: "90px",
                paddingTop: "1px",
                maxWidth: "90%",
                userSelect: "text", // Make the text selectable
                zIndex: 1108,
              }}
            >
              <p
                style={{
                  backgroundColor: "#e6e6e6",
                  padding: "10px",
                  borderRadius: "6px",
                  // border: '1px solid black',
                  margin: "10px",
                  userSelect: "text",
                }}
              >
                {message.answer}
              </p>
             
            </div>
          </div>
        ))}
        {/* {topdoctors && topdoctors.map((doctor, index) => (
        <ContactCard key={index} doctor={doctor} />
      ))} */}
      </div>
      {/* <ContactList doctors={topdoctors} /> */}
      <form
        onSubmit={handleQuerySubmit}
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "14px",
          borderTop: "2px solid #BCBCBC ",
        }}
      >
        <div style={{ marginRight: "10px" }}>
          <PostAddIcon onClick={handlePrescriptionSubmit} />
        </div>
        <input
          type="text"
          id="query"
          name="query"
          placeholder="Write your question..."
          value={query}
          onChange={handleQuestionChange}
          style={{
            height: "50px",
            width: "100%",
            padding: "12px 20px",
            margin: "0",
            display: "inline-block",
            border: "1px solid #BCBCBC",
            borderRadius: "5px",
            boxSizing: "border-box",
            outline: "none",
            backgroundColor: "white",
          }}
        />
        {!queryInProgress && (
          <Button
            type="submit"
            variant="contained"
            // endIcon={<SendIcon />}
            aria-label="send"
            style={{
              backgroundColor: "#fff",
              marginTop: "3px",
              marginLeft: "8px",
            }}
            disabled={!query}
          >
            <SendIcon sx={{ color: "black" }} />
          </Button>
        )}
      </form>
      {/*<Typography variant="h5" gutterBottom>
            Upload File
          </Typography>
          <input type="file" onChange={handleFileChange} />
          <Tooltip
            title="supports .txt, .docx, .pptx, .pdf, .xlsx"
            placement="right"
          >
            <Button
              variant="contained"
              onClick={handleUploadSubmit}
              style={{ marginLeft: "10px" }}
            >
              <FileUploadIcon style={{ marginRight: "4px" }} />
              Upload
            </Button>
            </Tooltip>*/}
      <Dialog open={openModal} onClose={handleCloseModal} className="dialog-container">
      <DialogTitle className="dialog-title">Upload Prescription</DialogTitle>
      <DialogContent className="dialog-content">
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileUpload}
          className="file-input"
        />
        <div className="checkbox-container">
          <FormControlLabel
            control={<Checkbox checked={isPrescription} onChange={() => setIsPrescription(!isPrescription)} color="primary" />}
            label="Prescription"
          />
          <FormControlLabel
            control={<Checkbox checked={!isPrescription} onChange={() => setIsPrescription(!isPrescription)} color="primary" />}
            label="Report"
          />
        </div>
      </DialogContent>
      <DialogActions className="dialog-actions">
        <Button onClick={handleCloseModal} className="cancel-button">Cancel</Button>
      </DialogActions>
    </Dialog>
    </div>
  );
};

export default MedicalChatbot;
