export async function getAdmin (req, res) {
  try {
    res.status(200).send(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
          <meta name="theme-color" content="#000000">
          <title>Seasoning</title>
        </head>
        <body>
          <noscript>
            You need to enable JavaScript to run this app.
          </noscript>
          <div id="root"></div>
          <script src="/app.js"></script>
        </body>
      </html>`
    )
  } catch (err) {
    res.status(500)
  }
}
