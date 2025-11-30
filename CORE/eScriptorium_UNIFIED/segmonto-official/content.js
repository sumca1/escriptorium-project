document.addEventListener("DOMContentLoaded", function() {
  const regex =
    /(?<domain>.*)\/document(?:s?)\/(?<document>\d+)(?:\/parts?\/(?<page>\d+))?/;
  const re_zones =
    /^(CustomZone|DamageZone|GraphicZone|DigitizationArtefactZone|DropCapitalZone|MainZone|MarginTextZone|MusicZone|NumberingZone|QuireMarksZone|RunningTitleZone|SealZone|StampZone|TableZone|TitlePageZone)(\:.*)?(#.*)?$/;
  const re_lines =
    /^(CustomLine|DefaultLine|DropCapitalLine|HeadingLine|InterlinearLine|MusicLine)(\:.*)?(#.*)?$/;
  const form = document.getElementById("form");
  const results = document.getElementById("results");
  /**
   * Parses an URI and returns its domain.
   * @param {string} uri - A full URI
   * @returns {string} The domain of the URI
   */
  function getDomain(uri) {
    const url = new URL(uri);
    return url.hostname;
  }
  /**
   * Request permissions for the current domain, so that CORS
   *  are enabled
   * @param {string} domain - The domain of the current page
   * @rreturns {bool} The status of the permission
   */
  async function requestPermissions(domain) {
    const response = await chrome.permissions.request({
      origins: [`https://${domain}/*`]
    });
    return ((response) ? true : false);
  }
  chrome.tabs.query({
    active: true,
    currentWindow: true
  }, function(tabs) {
    const currentUrl = tabs[0].url;
    document.getElementById("url").value = currentUrl;
    const token = localStorage.getItem("api-token-" + getDomain(currentUrl));
    // You can now use the currentUrl as needed
    if (token !== undefined) {
      document.getElementById("auth-token").value = token;
    }
  });

  function humanUri(originalUri) {
    const m = regex.exec(originalUri);
    if (m.groups.page !== undefined) {
      return `${m.groups.domain.replace("\/api", "")}/document/${m.groups.document}/part/${m.groups.page}/edit/`;
    } else {
      return `${m.groups.domain.replace("\/api", "")}/document/${m.groups.document}`;
    }
  }

  function addLoadingText(targetElement, text) {
    /** Add a loading text within targetElement. Returns the element
     * 
     */
    if (!targetElement) {
      console.error(`Element with id ${targetElement} not found.`);
      return;
    }
    const paragraph = document.createElement('p');
    paragraph.innerHTML =
      `${text}<span class="dot1">.</span><span class="dot2">.</span><span class="dot3">.</span>`;
    targetElement.appendChild(paragraph);
    return paragraph;
  }

  function transformArrayToObject(arr) {
    return arr.reduce((acc, obj) => {
      acc[obj.pk] = obj.name;
      return acc;
    }, {});
  }

  function createLine(ul, type, details) {
    const el = document.createElement("li");
    el.innerHTML = `- ${type} ${details}`;
    ul.appendChild(el);
  }

  function checkValidity(typology, type) {
    if (typology === undefined) {
      return false;
    } else if (type === "line" && re_lines.test(typology)) {
      return true;
    } else if (type === "zone" && re_zones.test(typology)) {
      return true;
    }
    return false;
  }

  function createUl(parent, title) {
    const ul = document.createElement("ul"),
      titleLi = document.createElement("li"),
      li = document.createElement("li"),
      ul2 = document.createElement("ul");
    ul.classList.add("list-unstyled");
    ul.style = "padding-left: 2em!important;";
    ul2.style = "padding-left: 3em!important;";
    ul.appendChild(titleLi);
    titleLi.innerText = title;
    ul.appendChild(li);
    li.appendChild(ul2);
    parent.appendChild(ul);
    return ul;
  }

  function createBadge(ul, sum, total, type) {
    const badge = document.createElement("li"),
      perc = ((total > 0) ? sum / total * 100 : 100.00).toFixed(2);
    if (perc == 100.00) {
      badge.innerHTML =
        `<span class="badge text-bg-success">${sum}/${total} ${type} are OK !</span>`;
    } else if (perc >= 50.00) {
      badge.innerHTML =
        `<span class="badge text-bg-warning">${sum}/${total} ${type} are OK.</span>`;
    } else {
      badge.innerHTML =
        `<span class="badge text-bg-danger">${sum}/${total} ${type} are OK...</span>`;
    }
    ul.appendChild(badge);
  }
  /**
   * 
   */
  async function authFetch(uri, token) {
    // Options de la requête
    const options = {
      method: 'GET',
      headers: {
        "Authorization": "Token " + token
      },
    };
    const uri_fetch = await fetch(uri, options);
    return uri_fetch;
  }
  async function processPart(page, token, typesDictionary) {
    const hURI = humanUri(page);
    const loadingText = addLoadingText(results,
      `Retrieving information from <a href="${hURI}">${hURI}</a>`);
    try {
      const response = await authFetch(page, token);
      if (!response.ok) {
        results.innerHTML =
          `<hr/><div class="alert alert-danger">HTTP error! Status: ${response.status}</div>`;
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      // Create the details
      loadingText.remove();
      const element = document.createElement(`p`);
      element.innerHTML = `Results for <a href="${hURI}">${hURI}</a>`;
      results.appendChild(element);
      // Create the list for zones
      const ulZone = createUl(element, "Regions");
      let zoneStats = 0;
      for (let i = 0; i < data.regions.length; i++) {
        let reg = data.regions[i];
        if (data.regions[i].typology === null) {
          createLine(ulZone, "Region", "has no types");
        } else if (checkValidity(typesDictionary.regions[reg.typology],
            "zone") !== true) {
          createLine(ulZone, `Region (ID ${reg.external_id})`,
            `has the invalid type ${typesDictionary.regions[reg.typology]}`
          );
        } else {
          zoneStats += 1;
        }
      }
      createBadge(ulZone, zoneStats, data.regions.length, "regions");
      const ulLine = createUl(element, "Lines");
      let lineStats = 0;
      for (let i = 0; i < data.lines.length; i++) {
        let line = data.lines[i],
          errors = 0;
        if (line.typology === null) {
          createLine(ulLine,
            `Line (ID ${line.external_id}, Order ${line.order+1})`,
            "has no types");
          errors += 1;
        } else if (checkValidity(typesDictionary.lines[line.typology],
            "line") !== true) {
          createLine(ulLine,
            `Line (ID ${line.external_id}, Order ${line.order+1})`,
            `has the invalid type ${typesDictionary.lines[line.typology]}.`
          );
          errors += 1;
        }
        if (line.region === undefined || line.region === null) {
          createLine(ulLine,
            `Line (ID ${line.external_id}, Order ${line.order+1})`,
            `does not belong to a region.`);
          errors += 1;
        }
        if (errors == 0) {
          lineStats += 1;
        }
      }
      createBadge(ulLine, lineStats, data.lines.length, "lines");
    } catch (error) {
      results.innerHTML =
        `<hr/><div class="alert alert-danger">Unable to reach the server.</div>`;
      console.error('Error fetching data:', error);
      // You can handle errors here or propagate them to the caller as needed
    }
  }
  async function retrievePartIds(domain, docId, token, callback) {
    try {
      const response = await authFetch(
        `${domain}/api/documents/${docId}/parts/`, token);
      if (!response.ok) {
        results.innerHTML =
          `<hr/><div class="alert alert-danger">HTTP error! Status: ${response.status}</div>`;
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      let pages = [];
      for (let i = 0; i < data.results.length; i++) {
        pages.push(
          `${domain}/api/documents/${docId}/parts/${data.results[i].pk}/`
        );
      }
      return callback(pages, token);
    } catch (error) {
      results.innerHTML =
        `<hr/><div class="alert alert-danger">Unable to reach the server.</div>`;
      console.error('Error fetching data:', error);
      // You can handle errors here or propagate them to the caller as needed
    }
  }
  async function processQueue(uris, token, typesDictionary) {
    for (const uri of uris) {
      await processPart(uri, token, typesDictionary);
    }
    console.log('Toutes les pages ont été traitées.');
  }
  /**
   * Parses a document specified by its URI and extracts information based on the provided pages parameter.
   * @param {string} domain - The domain of the eScriptorium server
   * @param {string} docId - The ID of the document to parse.
   * @param {string} pages - A string indicating which pages to extract. Can be a page number ('1', '2', etc.) or 'all' to extract all pages.
   * @param {string} token - Authentification token
   * @param {Function} callback - A callback function that takes a typesDictionary object and a uriList object as arguments.
   */
  async function parseDocument(domain, docId, pageMode, token, callback) {
    const loadingText = addLoadingText(results,
      "Retrieving the list of region and line types");
    loadingText.remove();
    authFetch(`${domain}/api/documents/${docId}/`, token)
      .then(response => {
        if (!response.ok) {
          results.innerHTML =
            `<hr/><div class="alert alert-danger">HTTP error! Status: ${response.status}</div>`;
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        // Assuming your JSON structure has 'pages' and 'objects' properties
        const typesDictionary = {
          "regions": transformArrayToObject(data.valid_block_types),
          "lines": transformArrayToObject(data.valid_line_types)
        };
        if (pageMode == "all") {
          retrievePartIds(domain, docId, token, (uris, token) => {
            callback(uris, token, typesDictionary);
          });
        } else {
          callback([
              `${domain}/api/documents/${docId}/parts/${pageMode}`
            ],
            token, typesDictionary);
        }
        // const objects = data.objects;
      })
      .catch(error => {
        results.innerHTML =
          `<hr/><div class="alert alert-danger">Unable to reach the server.</div>`;
        console.error('Error fetching data:', error);
        // You can handle errors here or propagate them to the caller as needed
      });
  }
  form.addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(form);
    const auth = formData.get("auth"),
      url = formData.get("url");

    requestPermissions(getDomain(url)).then(() => {
      // Serialize the form data
      localStorage.setItem('api-token-' + getDomain(url), auth);
      let m;
      if ((m = regex.exec(url)) !== null) {
        let pageMode = "all";
        if (m.groups.page !== undefined) {
          pageMode = m.groups.page;
        }
        results.innerHTML = "";
        results.appendChild(document.createElement("hr"));
        // Run baby run !
        parseDocument(m.groups.domain, m.groups.document, pageMode, auth,
          processQueue);
      } else {
        results.innerHTML =
          `<div class="alert alert-danger">The provided URI does not correspond to a valid Document or Page URI.</div>`;
        return;
      }
    });
  });
});