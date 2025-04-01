document.addEventListener("DOMContentLoaded", () => {
	const uploadBox = document.querySelector(".upload-box");
	const fileInput = document.getElementById("fileInput");
	const resultsSection = document.getElementById("results");
	const foodItemsList = document.getElementById("foodItems");
	const recipesContainer = document.getElementById("recipes");
	const loadingSpinner = document.querySelector(".loading");

	// Hide results section initially
	resultsSection.style.display = "none";
	loadingSpinner.style.display = "none";

	// Handle drag and drop events
	uploadBox.addEventListener("dragover", (e) => {
		e.preventDefault();
		uploadBox.style.borderColor = "#4CAF50";
	});

	uploadBox.addEventListener("dragleave", () => {
		uploadBox.style.borderColor = "#ccc";
	});

	uploadBox.addEventListener("drop", (e) => {
		e.preventDefault();
		uploadBox.style.borderColor = "#ccc";
		const files = e.dataTransfer.files;
		if (files.length > 0) {
			handleFile(files[0]);
		}
	});

	// Handle file input change
	fileInput.addEventListener("change", (e) => {
		if (e.target.files.length > 0) {
			handleFile(e.target.files[0]);
		}
	});

	// Handle file upload and processing
	function handleFile(file) {
		if (!file.type.startsWith("image/")) {
			alert("Please upload an image file.");
			return;
		}

		// Show loading spinner
		loadingSpinner.style.display = "block";
		resultsSection.style.display = "none";

		const formData = new FormData();
		formData.append("image", file);

		// Send image to backend for processing
		fetch("/analyze", {
			method: "POST",
			body: formData
		})
			.then((response) => {
				if (!response.ok) {
					return response.json().then((err) => {
						throw new Error(
							err.error || "An error occurred while processing the image"
						);
					});
				}
				return response.json();
			})
			.then((data) => {
				// Hide loading spinner
				loadingSpinner.style.display = "none";
				resultsSection.style.display = "block";

				// Display detected food items
				foodItemsList.innerHTML = "";
				if (data.detected_items && data.detected_items.length > 0) {
					data.detected_items.forEach((item) => {
						const li = document.createElement("li");
						li.textContent = item;
						foodItemsList.appendChild(li);
					});
				} else {
					const li = document.createElement("li");
					li.textContent = "No food items detected";
					foodItemsList.appendChild(li);
				}

				// Display recipe suggestions
				recipesContainer.innerHTML = "";
				if (data.recipes && data.recipes.length > 0) {
					data.recipes.forEach((recipe) => {
						const recipeCard = createRecipeCard(recipe);
						recipesContainer.appendChild(recipeCard);
					});
				} else {
					const noRecipes = document.createElement("div");
					noRecipes.className = "no-recipes";
					noRecipes.textContent = "No recipe suggestions available";
					recipesContainer.appendChild(noRecipes);
				}
			})
			.catch((error) => {
				console.error("Error:", error);
				loadingSpinner.style.display = "none";
				alert(
					error.message ||
						"An error occurred while processing the image. Please try again."
				);
			});
	}

	// Create recipe card element
	function createRecipeCard(recipe) {
		const card = document.createElement("div");
		card.className = "recipe-card";

		card.innerHTML = `
            <img src="${recipe.image}" alt="${recipe.title}">
            <div class="recipe-card-content">
                <h3>${recipe.title}</h3>
                <a href="${recipe.url}" target="_blank" class="choose-photo-btn">View Recipe</a>
            </div>
        `;

		return card;
	}

	// Click handler for upload box
	uploadBox.addEventListener("click", () => {
		fileInput.click();
	});
});
