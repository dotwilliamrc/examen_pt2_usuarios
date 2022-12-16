const getRequest = async () => {
	try {
		response = await fetch("/api")
		data = await response.json()
		const credits = document.querySelector("#header_credits")
		credits.innerHTML = `${ data.credits }C | ${ data.USD }$`
	} catch (error) {
		console.error(error)
	}
}

	getRequest()
	setInterval(() => {
	getRequest()
	}, 5000)
