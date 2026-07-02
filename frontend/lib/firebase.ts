import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup as firebaseSignInWithPopup, signOut as firebaseSignOut } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL,
};

// Initialize Firebase only if config is present, otherwise use mock
let app;
let auth: any;
let googleProvider: any;
let signInWithPopup: any;
let signOut: any;

try {
  if (firebaseConfig.apiKey && firebaseConfig.apiKey !== "your_firebase_api_key") {
    app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
    signInWithPopup = firebaseSignInWithPopup;
    signOut = firebaseSignOut;
  } else {
    throw new Error("Firebase config missing");
  }
} catch (e) {
  console.warn("Firebase not configured. Using mock auth for development.");
  let mockUser: any = null;
  let authListeners: any[] = [];
  
  auth = {
    onAuthStateChanged: (cb: any) => {
      authListeners.push(cb);
      cb(mockUser);
      return () => {
        authListeners = authListeners.filter((l) => l !== cb);
      };
    },
  } as any;
  googleProvider = {} as any;
  
  signInWithPopup = async () => {
    console.log("Firebase not configured. Mock login successful for development.");
    mockUser = { displayName: "Mock User", email: "mock@example.com", uid: "123" };
    authListeners.forEach((cb) => cb(mockUser));
    return { user: mockUser };
  };
  
  signOut = async () => {
    console.log("Mock signed out");
    mockUser = null;
    authListeners.forEach((cb) => cb(null));
  };
}

export { app, auth, googleProvider, signInWithPopup, signOut };
