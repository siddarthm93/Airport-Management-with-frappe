frappe.provide("custom.views");

custom.views.load_inline_form = async function (doctype, docname, link) {
	let sidebarToggled = false;

	const $formPane = $("#right-form-pane");
	const $listPane = $("#left-list-pane");
	const sidebar = document.querySelector(".layout-side-section");
	if (sidebar && !sidebarToggled) {
		sidebar.classList.toggle("hidden");
		sidebarToggled = true;
	}

	// Expand panes
	$formPane.css({ display: "block", width: "50%" });
	$listPane.css("width", "50%");

	$formPane.html(`<div class="text-muted p-3">Loading ${doctype}...</div>`);

	const container = document.getElementById("right-form-pane");
	if (!container) return;

	container.innerHTML = `<p class="text-muted">Loading...</p>`;

	try {
		// 1. Clear the container first
		container.innerHTML = "";
		// 2. Create Top Bar
		const topBar = document.createElement("div");
		topBar.className = "d-flex justify-content-between align-items-center m-3 border-bottom";

		// 3. Title showing docname
		const title = document.createElement("h5");
		title.textContent = `${docname}`;
		title.className = "mb-0";

		// 4. Button Group
		const btnGroup = document.createElement("div");
		// btnGroup.className = "d-flex row gap-2";

		// 5. Edit Button
		const editBtn = document.createElement("button");
		editBtn.className = "btn btn-sm btn-outline-primary rounded me-2";
		editBtn.innerHTML = `<i class="fa fa-edit"></i>`;

		// 6. Close Button
		const closeBtn = document.createElement("button");
		closeBtn.className = "btn btn-sm btn-outline-danger rounded";
		closeBtn.innerHTML = `<i class="fa fa-times"></i>`;

		// Button click handlers
		editBtn.onclick = () => {
			// fieldgroup.set_df_property("read_only", 0); // Makes fields editable
			if (link) {
				frappe.set_route(link.pathname);
				return false;
			}
		};
		closeBtn.onclick = () => {
			container.innerHTML = ""; // Closes the form view
			$formPane.css({ display: "none", width: "0" });
			$listPane.css("width", "100%");
			if (sidebar && sidebar.classList.contains("hidden")) {
				sidebar.classList.remove("hidden"); // Show the sidebar
				sidebarToggled = false;
			}
		};

		// 8. Append Buttons to Group and TopBar
		btnGroup.appendChild(editBtn);
		btnGroup.appendChild(closeBtn);
		topBar.appendChild(title);
		topBar.appendChild(btnGroup);

		// 9. Insert TopBar at the Top
		container.appendChild(topBar);

		// Get doc and meta
		const doc = await frappe.db.get_doc(doctype, docname);
		const meta = await frappe.get_meta(doctype);

		// Step 2: Enrich parent meta.fields with child table fields
		for (const field of meta.fields) {
			if (field.fieldtype === "Table" && field.options) {
				// Get child fields and assign to parent field
				const child_fields = frappe.meta.get_docfields(field.options);
				field.fields = child_fields;
				field.data = doc[field.fieldname] || [];
				field.cannot_add_rows = true;
				field.cannot_delete_rows = true;
				field.cannot_delete_all_rows = true;
				field.in_place_edit = true;
			}
		}

		// Create FieldGroup
		const fieldgroup = new frappe.ui.FieldGroup({
			fields: meta.fields,
			body: container,
		});

		fieldgroup.configure_columns = false;
		fieldgroup.open_form_button = false;
		await fieldgroup.make();
		fieldgroup.set_values(doc);
	} catch (e) {
		container.innerHTML = `<p class="text-danger">Error loading form.</p>`;
		console.error(e);
	}
};

frappe.listview_settings["Airplane Flight"] = {
	onload(listview) {
		const $frappeList = $(listview.page.body).find(".frappe-list");

		// Prevent duplicate injection
		if ($frappeList.find("#split-view-container").length) return;

		const $resultList = listview.$result.detach();

		// Create split view layout (only wrapping the result list)
		const $splitView = $(`
            <div id="split-view-container" class="d-flex w-100" style="min-height: 400px; overflow: hidden;">
                <div id="left-list-pane" class="flex-grow-1" style="overflow-y: auto; transition: width 0.3s; width: 100%;">
                    <div id="list-content-area"></div>
                </div>
                <div id="right-form-pane" style="width: 0; display: none; transition: width 0.3s; overflow-y: auto;"></div>
            </div>
        `);

		// Insert split view layout before the pagination controls
		$frappeList.find(".list-paging-area").before($splitView);

		// Append the result list into left pane
		$splitView.find("#list-content-area").append($resultList);

		// Add "View" buttons to each row
		setTimeout(() => {
			listview.$result
				.off("click", ".list-row, .image-view-header, .file-header")
				.on("click", ".list-row, .image-view-header, .file-header", (e) => {
					const $target = $(e.target);
					console.log("This is coming here");

					// tick checkbox if Ctrl/Meta key is pressed
					if ((e.ctrlKey || e.metaKey) && !$target.is("a")) {
						const $list_row = $(e.currentTarget);
						const $check = $list_row.find(".list-row-checkbox");
						$check.prop("checked", !$check.prop("checked"));
						e.preventDefault();
						this.on_row_checked();
						return;
					}
					// don't open form when checkbox, like, filterable are clicked
					if (
						$target.hasClass("filterable") ||
						$target.hasClass("select-like") ||
						$target.hasClass("file-select") ||
						$target.hasClass("list-row-like") ||
						$target.is(":checkbox")
					) {
						e.stopPropagation();
						return;
					}

					// link, let the event be handled via set_route
					if ($target.is("a")) return;

					// clicked on the row, open form
					const $row = $(e.currentTarget);

					const link = $row.find(".list-subject a").get(0);
					const linkPath = link.pathname;
					const name = linkPath.split("/")[3];

					custom.views.load_inline_form("Airplane Flight", name, link);

					// if (link) {
					// 	frappe.set_route(link.pathname);
					// 	return false;
					// }
				});
		}, 300);
	},
};
