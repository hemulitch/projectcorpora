// adding or deleting forms
const inputSets = document.querySelectorAll(".input-set");
const plusButton = document.getElementById("plus-button");

plusButton.addEventListener("click", () => {
    const hiddenSet = Array.from(inputSets).find(set => window.getComputedStyle(set).display === "none");
    
    if (hiddenSet) {
        hiddenSet.style.display = "block";
        if (hiddenSet === inputSets[inputSets.length - 1]) {
            plusButton.textContent = "-";
        }
    } else {
        inputSets.forEach(set => set.style.display = "none");
        inputSets[0].style.display = "block";
        plusButton.textContent = "+";
    }
});