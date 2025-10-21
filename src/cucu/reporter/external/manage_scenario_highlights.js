;
function fitHighlightToImage(highlightDiv) {
  console.log(highlightDiv);

  // Every highlight element is expected to have an ID of the form
  // <image ID>-highlight . Get the image ID here.
  const sliceEndIndex = highlightDiv.id.length - "-highlight".length;

  const targetImgId = highlightDiv.id.slice(0, sliceEndIndex);
  const targetImg = document.querySelector(`img#${targetImgId}`);
  const imgViewportRect = targetImg.getBoundingClientRect();
  // Compute absolute coordinates relative to the whole document
  const targetDimensions = {
    height: imgViewportRect["height"],
    width: imgViewportRect["width"],
    top: imgViewportRect["top"] + window.pageYOffset,
    left: imgViewportRect["left"] + window.pageXOffset,
  };

  const updatedHighlightStyle = [
    "position:absolute",
    `height:${targetDimensions["height"] * highlightDiv.getAttribute("height-ratio")}px`,
    `width:${targetDimensions["width"] * highlightDiv.getAttribute("width-ratio")}px`,
    `top:${(targetDimensions["height"] * highlightDiv.getAttribute("top-ratio")) + targetDimensions["top"]}px`,
    `left:${(targetDimensions["width"] * highlightDiv.getAttribute("left-ratio")) + targetDimensions["left"]}px`,
    "border:2px solid magenta",
    "border-radius:2px",
  ].join(";");
  highlightDiv.style = updatedHighlightStyle;
};

function resizeAllHighlights(){
  const highlights = document.querySelectorAll(".step-image-highlight");
  highlights.forEach(h => fitHighlightToImage(h));
};

// The <summary> elements make the DOM jump around.
// The delayed resizeAllHighlights helps make sure all the highlights
// from lower down the page get into the right place after things settle.
document.querySelectorAll("summary").forEach(
  e => {
    e.addEventListener("click", resizeAllHighlights);
    e.addEventListener(
      "click",
      () => setTimeout(resizeAllHighlights, 10)
    );
  }
);
// The td.data-toggles cause an animation that takes a lot longer than
// the one from the <summary> elements. As before, the fast
// resizeAllHighlights makes the ones the user can see first jump into
// place, then the delayed one helps put the ones lower down into place.
document.querySelectorAll("td[data-toggle=collapse").forEach(
  e => {
    e.addEventListener(
      "click",
      () => setTimeout(resizeAllHighlights, 10)
    );
    e.addEventListener(
      "click",
      // 400ms value was determined experimentally.
      // It's approximately the duration of the animation triggered
      // by clicking on these elements
      () => setTimeout(resizeAllHighlights, 400)
    );
  }
);
window.onload = resizeAllHighlights;
window.onresize = resizeAllHighlights;
