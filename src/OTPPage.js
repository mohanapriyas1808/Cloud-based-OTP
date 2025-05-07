import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function OTPPage() {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // ✅ Generate OTP Function
  const handleGenerateOTP = async () => {
    setMessage("");
    setLoading(true);
    try {
      const response = await axios.post(
        "https://vc24xdk61m.execute-api.ap-south-1.amazonaws.com/prod/generate",
        { email },
        {
          headers: {
            "Content-Type": "application/json; charset=utf-8",
          },
        }
      );
      console.log("Generate OTP response:", response.data);
      setMessage("OTP sent to your email.");
    } catch (err) {
      console.error("Error sending OTP:", err.response?.data || err.message);
      setMessage("Failed to send OTP. Please try again.");
    }
    setLoading(false);
  };

  // ✅ Verify OTP Function
  const handleVerifyOTP = async () => {
    setMessage("");
    setLoading(true);
    try {
      const response = await axios.post(
        "https://vc24xdk61m.execute-api.ap-south-1.amazonaws.com/prod/verify",
        { email, otp },
        {
          headers: {
            "Content-Type": "application/json; charset=utf-8",
          },
        }
      );
      console.log("Verify OTP response:", response.data);
  
      // ✅ Correct navigation after OTP verification
      if (response.data && response.data.message === "OTP Verified Successfully!") {
        setMessage("OTP verified successfully.");
        navigate("/ai"); // Changed from "/dashboard" to "/ai"
      } else {
        setMessage("Invalid OTP. Please try again.");
      }
    } catch (err) {
      console.error("Error verifying OTP:", err.response?.data || err.message);
      setMessage("Error verifying OTP. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>OTP Verification</h2>

      <input
        type="email"
        placeholder="Enter email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ marginBottom: "10px", display: "block", padding: "8px" }}
      />
      <button onClick={handleGenerateOTP} disabled={loading}>
        {loading ? "Sending OTP..." : "Generate OTP"}
      </button>

      <input
        type="text"
        placeholder="Enter OTP"
        value={otp}
        onChange={(e) => setOtp(e.target.value)}
        style={{ margin: "10px 0", display: "block", padding: "8px" }}
      />
      <button onClick={handleVerifyOTP} disabled={loading}>
        {loading ? "Verifying..." : "Verify OTP"}
      </button>

      <p style={{ color: "blue", marginTop: "10px" }}>{message}</p>
    </div>
  );
}

export default OTPPage; // ✅ Fixed syntax error
