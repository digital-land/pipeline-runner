const processHTML = {
	preprocess(text, filename) {
		const quote = '\''
		const processed = text
			// replace jinja comments with js comments
			.replace(/\{#([\s\S]*?)#\}/g, (str, val) => `/*${val}*/`)
			// treat if-else statement as ( ... , ... )
			.replace(/\{%(-?\s*if.*?)%\}/g, (str, val) => `(/*${val.substr(1)}*/`)
			.replace(/\{%(-?\s*(else|elif).*?)%\}/g, (str, val) => `,/*${val.substr(1)}*/`)
			.replace(/\{%(-?\s*endif\s*-?)%\}/g, (str, val) => `/*${val.substr(1)}*/)`)
			// replace jinja statements with js comments
			.replace(/\{%(.*?)%\}/g, (str, val) => `/*${val}*/`)
			// replace jinja expression tags in strings with spaces
			.replace(/\{[{%]([\s\S]*?)[}%]\}/g, str => str.replace(/['"]/g, ' '))
			.replace(/(['"])(.*?)\1/g, str => str.replace(/(\{\{|\}\})/g, '  '))
			// replace jinja expressions with strings
			.replace(/\{\{(.*?)\}\}/g, (str, val) => `${quote} ${val} ${quote}`)
		return [processed]
	},

	postprocess(messages) {
		return messages[0]
	},
}

module.exports = {
	processors: {
		'.js': processHTML,
		'.html': processHTML,
		'.htm': processHTML,
	},
}
