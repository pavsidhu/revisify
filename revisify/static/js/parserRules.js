var wysihtml5ParserRules = {
  tags: {
    strong: {},
    b:      {},
    i:      {},
    em:      {},
    sub:    {},
    sup:    {},
    br:     {},
    p:      {},
    div:    {},
    span:   {},
    ul:     {},
    li:     {},
    a:      {
      set_attributes: {
        target: "_blank",
        rel:    "nofollow",
        class:  "underline"
      },
      check_attributes: {
        href:   "url" // important to avoid XSS
      }
    },
    img:    {
      set_attributes: {
        alt:     "image"
      },
      check_attributes: {
        src:     "url"
      }

    }
  }
};
