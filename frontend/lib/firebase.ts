import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup as firebaseSignInWithPopup, signOut as firebaseSignOut } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Only initialize Firebase on the client side (browser) to prevent SSR crashes
const isConfigured =
  typeof window !== "undefined" &&
  !!firebaseConfig.apiKey &&
  firebaseConfig.apiKey !== "undefined";

let app: any;
let auth: any;
let googleProvider: any;
let signInWithPopup: any;
let signOut: any;

if (isConfigured) {
  // Real Firebase path — used when keys are in .env.local
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
  auth = getAuth(app);
  googleProvider = new GoogleAuthProvider();
  signInWithPopup = firebaseSignInWithPopup;
  signOut = firebaseSignOut;
  console.log("Firebase initialized with real credentials.");
} else {
  // Mock auth for local development — simulates logged-in state
  console.log("Firebase not configured. Using mock auth for development.");

  let mockUser: any = null;
  let authListeners: any[] = [];

  auth = {
    onAuthStateChanged: (cb: any) => {
      authListeners.push(cb);
      // In development, auto-login as a mock MP user after a short delay
      if (typeof window !== "undefined") {
        setTimeout(() => {
          mockUser = {
            uid: "dev-mp-user-001",
            email: "mp@janaawaaz.dev",
            displayName: "Dev MP User",
            photoURL: null,
          };
          authListeners.forEach((l) => l(mockUser));
        }, 500);
      }
      return () => {
        authListeners = authListeners.filter((l) => l !== cb);
      };
    },
    currentUser: null,
  };

  googleProvider = {};

  signInWithPopup = async (_auth: any, _provider: any) => {
    mockUser = {
      uid: "dev-mp-user-001",
      email: "mp@janaawaaz.dev",
      displayName: "Dev MP User",
      photoURL: null,
    };
    authListeners.forEach((l) => l(mockUser));
    return { user: mockUser };
  };

  signOut = async (_auth: any) => {
    mockUser = null;
    authListeners.forEach((l) => l(null));
  };
}

export { app, auth, googleProvider, signInWithPopup, signOut };
