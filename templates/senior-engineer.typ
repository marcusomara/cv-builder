#set page(paper: "a4", margin: (x: 17mm, y: 14mm))
#set text(font: "New Computer Modern Sans", size: 9.2pt, fill: black)
#set par(justify: false, leading: 0.52em)
#set list(indent: 11pt, body-indent: 4pt, spacing: 2.5pt)
#show heading.where(level: 2): it => block(above: 8pt, below: 4pt, sticky: true)[
  #set text(size: 10.5pt, weight: "bold")
  #smallcaps(it.body)
  #line(length: 100%, stroke: 0.6pt)
]
#let entry(title, meta, body) = block(above: 4pt, below: 3pt, breakable: false)[
  #grid(columns: (1fr, auto), gutter: 8pt,
    text(weight: "bold")[#title], text(size: 8.5pt)[#meta])
  #body
]

%%HEADER%%
%%PAGE_ONE%%
#pagebreak()
%%PAGE_TWO%%
