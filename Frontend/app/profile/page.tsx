"use client";
import { useState, useEffect } from 'react';
import Navbar from "../components/navbar";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { redirect } from 'next/navigation'
const Profile = () => {
  const [avatarPreview, setAvatarPreview] = useState("");
  const [userData, setUserData] = useState({
    full_name: '',
    bio: '',
    avatar: ''
  });
  useEffect(() => {
    fetch("/profile/api")
      .then(response => response.json())
      .then(data => {
        if (!data.loggedIn) redirect("/login");
        setUserData({ full_name: data.data.full_name, bio: data.data.bio, avatar: data.data.avatar });
        setAvatarPreview(data.data.avatar+"?_="+(new Date()).getTime());
      });
  }, []);

  const handleInputChange = (field: any, value: any) => {
    setUserData({ ...userData, [field]: value });
  };

  const handleSave = () => {
    const formData = new FormData();
    formData.append("full_name", userData.full_name);
    formData.append("bio", userData.bio);
    formData.append("avatar", avatarPreview);
    fetch("/profile/api", {
      method: 'PUT',
      body: formData
    })
      .then(res => res.json())
      .then(data => toast(data.status))
      .catch(err => toast("Internal error, try again!"));
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
    <div className="min-h-screen flex">
      <Navbar />
      <main className="p-4 w-full">
        <h2>Profile</h2>
        <div className="space-y-2 flex flex-col m-8">
          <label
            htmlFor="avatar"
            className="w-20 h-20 rounded-full bg-gray-200 cursor-pointer flex items-center justify-center overflow-hidden"
          >
            <img
              src={avatarPreview || "/placeholder.png"}
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
          <input type="text" id="fullname" placeholder="Enter Full Name" className="rounded p-2 drop-shadow-lg" value={userData.full_name} onChange={e => handleInputChange('full_name', e.target.value)} />

          <label>Bio</label>
          <textarea id="bio" placeholder="Enter Bio" className="rounded p-2 drop-shadow-lg" value={userData.bio} onChange={e => handleInputChange('bio', e.target.value)} />

          <button className="bg-sky-600 w-fit px-4" onClick={() => handleSave()}>Save</button>
          <div>
          </div>
        </div>
        <ToastContainer />
      </main>
    </div>
  )
}

export default Profile;