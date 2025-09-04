  // Fetching all the required elements from DOM
  const userInput = document.getElementById("user-input");
  const submitBtn = document.getElementById("submit-btn");
  const errorMessage = document.getElementById("error-message");
  const header = document.getElementById("header");
  const sliderSection = document.getElementById("slider-section");
  const emotionMessage = document.getElementById("emotion-message");
  const sliderContainer = document.getElementById("slider-container");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  // Memes array is used for storing the generated memes
  // CurrentIndex is used to keep track of the current image for the slider's functionality
  let memes = [];
  let currentIndex = 0;

  // Error messages in case there is no input
  function showError(text) {
    errorMessage.textContent = text;
    errorMessage.style.display = "block";
  }
  function clearError() {
    errorMessage.style.display = "none";
  }
  
  // This function resizes the container based on the current img, since the images are of different
  // dimensions
  function resizeContainer() {
    const activeImg = sliderContainer.querySelector("img.active");
    if (!activeImg) return;
    const display = (activeImg.naturalHeight / activeImg.naturalWidth) * sliderContainer.clientWidth;
    sliderContainer.style.height = display + "px";
  }

  // Basic slider functionality
  function showIndex(index) {
    const allImgs = sliderContainer.querySelectorAll("img");
    if (allImgs.length === 0) return;
    if (index < 0) index = allImgs.length - 1;
    if (index >= allImgs.length) index = 0;
    currentIndex = index
    allImgs.forEach((img) => img.classList.remove("active"));
    const toShow = allImgs[index];
    toShow.classList.add("active");
    if (toShow.complete) {
      resizeContainer();
    } else {
      toShow.onload = resizeContainer;
    }
  }
  // Basic slider functionality part 2
  function loadSlider(urlArray) {
    const existing = sliderContainer.querySelectorAll("img");
    existing.forEach((img) => img.remove());
    memes = urlArray.slice();
    memes.forEach((url, idx) => {
      const img = document.createElement("img");
      img.src = url;
      img.classList.add("slide-image");
      if (idx == 0) {
        img.classList.add("active");
      }
      img.onload = () => {
        if (idx == 0) {
          resizeContainer();
        }
      };
      sliderContainer.appendChild(img);
    });
  }

  // Buttons to move around the slider imgs
  prevBtn.addEventListener("click", () => {
    showIndex(currentIndex - 1);
  });
  nextBtn.addEventListener("click", () => {
    showIndex(currentIndex + 1);
  });
  
  // Handling the user input and showing the appropriate txt based on the confidence
  // percentage of the prediction
  function handleSubmit() {
    const text = userInput.value.trim();
    if (!text) {
      showError("Please enter a sentence before submitting.");
      return;
    }
    clearError();
    header.classList.add("shrink");
    fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((data) => Promise.reject(data));
        return res.json();
      })
      .then((data) => {
        let emotion = data.emotion;
        let confidence = data.confidence;
        let urls = data.memes;
        if (confidence < 50) {
          emotionMessage.textContent = `This is a hard one. Our best guess is ${emotion} with ${confidence}% confidence!`;
        } else {
          emotionMessage.textContent = `We got you! We are ${confidence}% sure the emotion is ${emotion}.`;
        }
        sliderSection.style.display = "flex";
        loadSlider(urls);
      })
      .catch((err) => {
        if (err.error) {
          showError(err.error);
        } else {
          alert("Something went wrong. Please try again.");
          console.error(err);
        }
      });
  }

  // Functions to submit the input, both with mouse and keyboard
  submitBtn.addEventListener("click", (e) => {
    e.preventDefault();
    handleSubmit();
  });

  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  });

  window.addEventListener("resize", () => {
    const activeImg = sliderContainer.querySelector("img.active");
    if (activeImg && activeImg.complete) {
      resizeContainer();
    }
  });
