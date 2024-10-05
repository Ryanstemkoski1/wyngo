toggleFavorite = async (id, type, el) => {
    const payload = {
        id,
        type,
    }
    const url = "/api/toggle-wishlist/"
    try {
        const result = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            redirect: "follow",
            body: JSON.stringify(payload),
        })
        if (result.status === 403) {
            location.href = '/login/'
        }
        if (result.status === 200) {
            const data = await result.json()
            const added = data.added
            if (added) {
                el.firstElementChild.classList.add('fill-white')
            } else {
                el.firstElementChild.classList.remove('fill-white')
            }
        }
    } catch (error) {
        console.log(error)
    }
}
