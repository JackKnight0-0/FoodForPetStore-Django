const mainProductImage = document.getElementById('main-product-image')
const thumbnailImages = document.getElementById('thumbnail').children
for (let i = 0; i < thumbnailImages.length; i++) {
    thumbnailImages[i].children[0].addEventListener('click', (event) => {
        mainProductImage.src = event.target.src
    })
}


const ingredientButton = document.getElementById('ingredients-button')
const directionButton = document.getElementById('direction-button')

const ingredientContent = document.getElementById('ingredients-content')
const directionContent = document.getElementById('direction-content')

ingredientButton.addEventListener('click', function (event) {
    if (!ingredientButton.classList.contains('active')) {
        ingredientButton.classList.add('active')
        directionButton.classList.remove('active')
        directionContent.classList.remove('show', 'active')
        ingredientContent.classList.add('show', 'active')


    }
})

directionButton.addEventListener('click', function (event) {
    if (!directionContent.classList.contains('active')) {
        directionButton.classList.add('active')
        ingredientButton.classList.remove('active')
        ingredientContent.classList.remove('show', 'active')
        directionContent.classList.add('show', 'active')

    }
})