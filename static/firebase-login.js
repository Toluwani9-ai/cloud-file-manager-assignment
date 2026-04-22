"use strict";

// Firebase imports
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.9.0/firebase-app.js";
import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut
} from "https://www.gstatic.com/firebasejs/12.9.0/firebase-auth.js";

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyBSOis4txhY7y3wRhOUrean__LoLQk6H0M",
  authDomain: "cloud-assignment-b3c4b.firebaseapp.com",
  projectId: "cloud-assignment-b3c4b",
  storageBucket: "cloud-assignment-b3c4b.appspot.com",
  messagingSenderId: "970871834625",
  appId: "1:970871834625:web:86c1716065c9d9ed6e5800",
  measurementId: "G-1ZG3KF9VX0"
};

window.addEventListener("load", function () {

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);

    updateUI(document.cookie);


    //Sign up
    document.getElementById("sign-up").addEventListener("click", async function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            const token = await user.getIdToken();
            document.cookie = "token=" + token + ";path=/;SameSite=Strict";

            window.location.reload();
        } catch (error) {
            alert(error.message);
            console.error(error);
        }
    });


    // Login
    document.getElementById("login").addEventListener("click", async function () {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            const token = await user.getIdToken();
            document.cookie = "token=" + token + ";path=/;SameSite=Strict";

            window.location.reload();
        } catch (error) {
            alert(error.message);
            console.error(error);
        }
    });


    document.getElementById("sign-out").addEventListener("click", async function () {
        await signOut(auth);

        document.cookie = "token=;path=/;SameSite=Strict";
        window.location.reload();
    });


    // Create folder
    const createFolderBtn = document.getElementById("create-folder");

    if (createFolderBtn) {
        createFolderBtn.addEventListener("click", async function () {
            const name = document.getElementById("folder-name").value;

            if (!name) {
                alert("Enter folder name");
                return;
            }

            try {
                const res = await fetch("/create-folder", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        folder_name: name
                    })
                });

                const data = await res.json();

                if (data.message) {
                    alert(data.message);
                    window.location.reload(); // refresh to see update
                } else {
                    alert(data.error);
                }

            } catch (err) {
                console.error(err);
                alert("Something went wrong");
            }
        });
    }

});


// Ui update

function updateUI(cookie) {
    const token = parseCookieToken(cookie);

    if (token.length > 0) {
        document.getElementById("login-box").hidden = true;
        document.getElementById("user-box").hidden = false;
    } else {
        document.getElementById("login-box").hidden = false;
        document.getElementById("user-box").hidden = true;
    }
}


//Cookie
function parseCookieToken(cookie) {
    const parts = cookie.split(";");

    for (let i = 0; i < parts.length; i++) {
        const keyValue = parts[i].split("=");

        if (keyValue[0].trim() === "token") {
            return keyValue[1];
        }
    }

    return "";
}