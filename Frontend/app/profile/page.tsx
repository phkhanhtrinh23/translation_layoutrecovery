"use client";
import { useState, useEffect } from 'react';
import Navbar from "../components/navbar";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { redirect } from 'next/navigation'

const Profile = () => {
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [userData, setUserData] = useState({
    fullname: '',
    bio: ''
  });
  useEffect(() => {
    // Fetch user data from the API
    fetch("/profile/api") // Replace with your actual API endpoint
      .then(response => response.json())
      .then(data => {
        if (!data.loggedIn) redirect("/login");
        setUserData({ fullname: data.fullname, bio: data.bio });
        setAvatarPreview(data.avatar);
      });
  }, []);

  const handleInputChange = (field: any, value: any) => {
    setUserData(prevData => ({
      ...prevData,
      [field]: value
    }));
  };

  const handleSave = () => {
    // Send updated user data to the API for saving
    fetch("/api/profile", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fullname: userData.fullname,
        bio: userData.bio,
        avatar: avatarPreview
      })
    })
      .then(response => response.json())
      .then(data => toast(data.status))
      .catch(err => toast(err));
  };

  const previewImage = (input: any) => {
    const file = input.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e: any) {
        setAvatarPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };
  return (
    <div className="h-screen flex">
      <Navbar />
      <main className="p-4 w-full">
        <h2>Profile</h2>
        <div className="space-y-2 flex flex-col m-8">
          <label
            htmlFor="avatar"
            className="w-20 h-20 rounded-full bg-gray-200 cursor-pointer flex items-center justify-center overflow-hidden"
          >
            <img
              src={avatarPreview || '/avatar-placeholder.jpg'}
              alt="Avatar"
              className="rounded-full w-full h-full object-cover"
            />
            <input
              type="file"
              id="avatar"
              className="hidden"
              accept="image/*"
              onChange={(e) => previewImage(e.target)}
            />
          </label>
          <label>Full Name</label>
          <input type="text" id="fullname" placeholder="Enter Full Name" className="rounded p-2" value={userData.fullname} onChange={e => handleInputChange('fullname', e.target.value)} />

          <label>Bio</label>
          <textarea id="bio" placeholder="Enter Bio" className="rounded p-2" value={userData.bio} onChange={e => handleInputChange('bio', e.target.value)} />

          <button className="bg-sky-600" onClick={() => handleSave()}>Save</button>
          <div>
          </div>
        </div>
        <ToastContainer />
      </main>
    </div>
  )
}

export default Profile;