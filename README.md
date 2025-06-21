# Deploying the BirdNET Server

This guide provides instructions on how to deploy the Python-based BirdNET server to a cloud platform called [Render](https://render.com/), so it can be accessed publicly by your iOS app. Render has a free tier that is suitable for this project.

## Step 1: Push to GitHub

1.  **Create a GitHub Account:** If you don't have one, sign up at [github.com](https://github.com).
2.  **Create a New Repository:** Create a new public repository on GitHub. Let's call it `birdnet-server`.
3.  **Upload Files:** Upload the contents of your local `birdnet-server` directory (`main.py`, `requirements.txt`, and this `README.md`) to the new GitHub repository.

## Step 2: Deploy on Render

1.  **Create a Render Account:** If you don't have one, sign up at [render.com](https://render.com) using your GitHub account.

2.  **Create a New Web Service:**
    *   On your Render dashboard, click **"New +"** and select **"Web Service"**.
    *   Connect your GitHub account and select your `birdnet-server` repository.

3.  **Configure the Service:**
    *   **Name:** Give your service a name (e.g., `birdnet-server`). This will be part of its public URL.
    *   **Region:** Choose a region close to you.
    *   **Branch:** Select `main` (or `master`).
    *   **Root Directory:** Leave this blank.
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt` (this should be the default).
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
    *   **Instance Type:** Select the `Free` plan.

4.  **Deploy:** Click **"Create Web Service"**. Render will automatically pull your code from GitHub, build it, and deploy it. The first build might take a few minutes.

## Step 3: Update the iOS App

1.  **Get Your Public URL:** After a successful deployment, Render will provide you with a public URL for your service (e.g., `https://birdnet-server.onrender.com`).

2.  **Update `BirdNetService.swift`:**
    *   Open the `BirdSoundIdentifier` Xcode project.
    *   Navigate to `BirdSoundIdentifier/Services/BirdNetService.swift`.
    *   Replace the placeholder URL with your new public URL from Render.

    Your updated code should look like this:
    ```swift
    // Before
    // private let birdnetServerURL = URL(string: "http://YOUR_LOCAL_IP:8000/analyze")!

    // After
    private let birdnetServerURL = URL(string: "https://<your-service-name>.onrender.com/analyze")!
    ```

That's it! Your app will now be able to communicate with your live, public-facing server for bird sound analysis. 