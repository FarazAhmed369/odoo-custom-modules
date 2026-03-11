import { hasTouch, isIosApp, isMacOS } from "@web/core/browser/feature_detection";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";
import { useSortable } from "@web/core/utils/sortable_owl";

import {
    Component,
    useExternalListener,
    onMounted,
    onPatched,
    onWillUpdateProps,
    useState,
    useRef,
} from "@odoo/owl";

class FooterComponent extends Component {
    static template = "ica_web_responsive.HomeMenu.CommandPalette.Footer";
    static props = {
        //prop added by the command palette
        switchNamespace: { type: Function, optional: true },
    };

    setup() {
        this.controlKey = isMacOS() ? "COMMAND" : "CONTROL";
    }
}
/**
 * Home menu
 *
 * This component handles the display and navigation between the different
 * available applications and menus.
 * @extends Component
 */
export class HomeMenu extends Component {
    static template = "ica_web_responsive.HomeMenu";
    static components = {  };
    static props = {
        apps: {
            type: Array,
            element: {
                type: Object,
                shape: {
                    actionID: Number,
                    href: String,
                    appID: Number,
                    id: Number,
                    label: String,
                    parents: String,
                    webIcon: {
                        type: [
                            Boolean,
                            String,
                            {
                                type: Object,
                                optional: 1,
                                shape: {
                                    iconClass: String,
                                    color: String,
                                    backgroundColor: String,
                                },
                            },
                        ],
                        optional: true,
                    },
                    webIconData: { type: String, optional: 1 },
                    xmlid: String,
                },
            },
        },
        reorderApps: { type: Function },
    };

    /**
     * @param {Object} props
     * @param {Object[]} props.apps application icons
     * @param {number} props.apps[].actionID
     * @param {number} props.apps[].id
     * @param {string} props.apps[].label
     * @param {string} props.apps[].parents
     * @param {(boolean|string|Object)} props.apps[].webIcon either:
     *      - boolean: false (no webIcon)
     *      - string: path to Odoo icon file
     *      - Object: customized icon (background, class and color)
     * @param {string} [props.apps[].webIconData]
     * @param {string} props.apps[].xmlid
     * @param {function} props.reorderApps
     */
    setup() {
        this.command = useService("command");
        this.menus = useService("menu");
        this.homeMenuService = useService("home_menu");
        this.ui = useService("ui");
        this.orm = useService("orm");
        this.state = useState({
            focusedIndex: null,
            isIosApp: isIosApp(),
            showTrialBanner: false,
            bannerTitle: "",
            bannerMessage: "",
            showLicenseBanner: false,
            licenseBannerTitle: "",
            licenseBannerMessage: "",
            licenseBannerType: "warning",
        });
        this.inputRef = useRef("input");
        this.rootRef = useRef("root");
        this.pressTimer;

        if (!this.env.isSmall) {
            this._registerHotkeys();
        }

        useSortable({
            enable: this._enableAppsSorting,
            // Params
            ref: this.rootRef,
            elements: ".o_draggable",
            cursor: "move",
            delay: 500,
            tolerance: 10,
            // Hooks
            onWillStartDrag: (params) => this._sortStart(params),
            onDrop: (params) => this._sortAppDrop(params),
        });

        onWillUpdateProps(() => {
            // State is reset on each remount
            this.state.focusedIndex = null;
        });

        onMounted(() => {
            if (!hasTouch()) {
                this._focusInput();
            }
            this._checkSubscriptionStatus();
            this._loadSubscriptionInfo();
            this._loadLicenseAndExpiryInfo();
        });

        onPatched(() => {
            if (this.state.focusedIndex !== null && !this.env.isSmall) {
                const selectedItem = document.querySelector(".o_home_menu .o_menuitem.o_focused");
                // When TAB is managed externally the class o_focused disappears.
                if (selectedItem) {
                    // Center window on the focused item
                    selectedItem.scrollIntoView({ block: "center" });
                }
            }
        });
    }

    //--------------------------------------------------------------------------
    // Getters
    //--------------------------------------------------------------------------

    /**
     * @returns {Object[]}
     */
    get displayedApps() {
        return this.props.apps;
    }

    /**
     * @returns {number}
     */
    get maxIconNumber() {
        const w = window.innerWidth;
        if (w < 576) {
            return 3;
        } else if (w < 768) {
            return 4;
        } else {
            return 6;
        }
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Object} menu
     * @returns {Promise}
     */
    _openMenu(menu) {
        return this.menus.selectMenu(menu);
    }

    /**
     * Update this.state.focusedIndex if not null.
     * @private
     * @param {string} cmd
     */
    _updateFocusedIndex(cmd) {
        const nbrApps = this.displayedApps.length;
        const lastIndex = nbrApps - 1;
        const focusedIndex = this.state.focusedIndex;
        if (lastIndex < 0) {
            return;
        }
        if (focusedIndex === null) {
            this.state.focusedIndex = 0;
            return;
        }
        const lineNumber = Math.ceil(nbrApps / this.maxIconNumber);
        const currentLine = Math.ceil((focusedIndex + 1) / this.maxIconNumber);
        let newIndex;
        switch (cmd) {
            case "previousElem":
                newIndex = focusedIndex - 1;
                break;
            case "nextElem":
                newIndex = focusedIndex + 1;
                break;
            case "previousColumn":
                if (focusedIndex % this.maxIconNumber) {
                    // app is not the first one on its line
                    newIndex = focusedIndex - 1;
                } else {
                    newIndex =
                        focusedIndex + Math.min(lastIndex - focusedIndex, this.maxIconNumber - 1);
                }
                break;
            case "nextColumn":
                if (focusedIndex === lastIndex || (focusedIndex + 1) % this.maxIconNumber === 0) {
                    // app is the last one on its line
                    newIndex = (currentLine - 1) * this.maxIconNumber;
                } else {
                    newIndex = focusedIndex + 1;
                }
                break;
            case "previousLine":
                if (currentLine === 1) {
                    newIndex = focusedIndex + (lineNumber - 1) * this.maxIconNumber;
                    if (newIndex > lastIndex) {
                        newIndex = lastIndex;
                    }
                } else {
                    // we go to the previous line on same column
                    newIndex = focusedIndex - this.maxIconNumber;
                }
                break;
            case "nextLine":
                if (currentLine === lineNumber) {
                    newIndex = focusedIndex % this.maxIconNumber;
                } else {
                    // we go to the next line on the closest column
                    newIndex =
                        focusedIndex + Math.min(this.maxIconNumber, lastIndex - focusedIndex);
                }
                break;
        }
        // if newIndex is out of bounds -> normalize it
        if (newIndex < 0) {
            newIndex = lastIndex;
        } else if (newIndex > lastIndex) {
            newIndex = 0;
        }
        this.state.focusedIndex = newIndex;
    }

    _focusInput() {
        if (!this.env.isSmall && this.inputRef.el) {
            this.inputRef.el.focus({ preventScroll: true });
        }
    }

    _enableAppsSorting() {
        return true;
    }

    /**
     * Load subscription info and calculate remaining trial days
     * @private
     */
//    async _loadSubscriptionInfo() {
//        try {
//            const trialStartDate = await this.orm.call(
//                "ir.config_parameter",
//                "get_param",
//                ["pos_subscription.trial_start_date"]
//            );
//            const trialDays = await this.orm.call(
//                "ir.config_parameter",
//                "get_param",
//                ["pos_subscription.trial_days"]
//            );
//
//            if (!trialStartDate || trialStartDate === "false" || !trialDays) {
//                return;
//            }
//
//            const startDate = new Date(trialStartDate);
//            const today = new Date();
//            const expiryDate = new Date(startDate);
//            expiryDate.setDate(expiryDate.getDate() + parseInt(trialDays));
//
//            const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
//
//            // Show banner only when 5 days or less are left
//            if (daysLeft <= 5 && daysLeft > 0) {
//                this.state.showTrialBanner = true;
//                this.state.bannerTitle = "Trial Period Active";
//                if (daysLeft === 1) {
//                    this.state.bannerMessage = `Your trial period expires tomorrow. You have 1 day left to activate a subscription.`;
//                } else {
//                    this.state.bannerMessage = `Your trial period expires in ${daysLeft} days. Please activate a subscription to continue using POS.`;
//                }
//            } else if (daysLeft === 0) {
//                this.state.showTrialBanner = true;
//                this.state.bannerTitle = "Trial Period Expiring Today";
//                this.state.bannerMessage = "Your trial period expires today. Please activate a subscription immediately.";
//            }
//            else if (daysLeft < 0) {
//                const expiredDays = Math.abs(daysLeft);
//                this.state.showTrialBanner = true;
//                this.state.bannerTitle = "Trial Period Expired";
//                this.state.bannerMessage =
//                    `Your trial period expired ${expiredDays} day${expiredDays > 1 ? 's' : ''} ago. Please activate a subscription to continue using POS.`;
//            }
//
//        } catch (error) {
//            console.warn("Could not load subscription info:", error);
//        }
//    }

    async _loadSubscriptionInfo() {
        try {
            const subscriptionType = await this.orm.call(
                "ir.config_parameter",
                "get_param",
                ["pos_subscription.subscription_type"]
            );

            const typeLabel = subscriptionType === "license" ? "License" : "Trial";

            let startDateStr, days = 0, expiryDate;

            if (subscriptionType === "trial") {
                startDateStr = await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["pos_subscription.trial_start_date"]
                );
                days = parseInt(await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["pos_subscription.trial_days"]
                ) || 0);

                if (!startDateStr || startDateStr === "false" || !days) {
                    return;
                }

                const startDate = new Date(startDateStr);
                expiryDate = new Date(startDate);
                expiryDate.setDate(expiryDate.getDate() + days);

            } else if (subscriptionType === "license") {
                startDateStr = await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["pos_subscription.license_start_date"]
                );
                days = parseInt(await this.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["pos_subscription.license_days"]
                ) || 0);

                if (!startDateStr || startDateStr === "false") {
                    return;
                }

                const startDate = new Date(startDateStr);
                expiryDate = new Date(startDate);
                expiryDate.setDate(expiryDate.getDate() + days);
            }

            const today = new Date();
            today.setHours(0, 0, 0, 0);
            expiryDate.setHours(0, 0, 0, 0);

            const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));

            if (daysLeft > 0 && daysLeft <= 10) {
                this.state.showTrialBanner = true;
                this.state.bannerTitle = `${typeLabel} Period Active`;
                this.state.bannerMessage = `Your ${typeLabel.toLowerCase()} period expires in ${daysLeft} day${daysLeft > 1 ? "s" : ""}. Please activate a subscription to continue using POS.`;
            } else if (daysLeft === 0) {
                this.state.showTrialBanner = true;
                this.state.bannerTitle = `${typeLabel} Period Expiring Today`;
                this.state.bannerMessage = `Your ${typeLabel.toLowerCase()} period expires today. Please activate immediately.`;
            } else if (daysLeft < 0) {
                const expiredDays = Math.abs(daysLeft);
                this.state.showTrialBanner = true;
                this.state.bannerTitle = `${typeLabel} Period Expired`;
                this.state.bannerMessage = `Your ${typeLabel.toLowerCase()} period expired ${expiredDays} day${expiredDays > 1 ? "s" : ""} ago. Please activate a subscription to continue using POS.`;
            }

        } catch (error) {
            console.warn("Could not load subscription info:", error);
        }
    }

    /**
     * Load license key and expiry date info combined
     * @private
     */
    async _loadLicenseAndExpiryInfo() {
        try {
            const licenseKey = await this.orm.call(
                "ir.config_parameter",
                "get_param",
                ["pos_subscription.license_key"]
            );

            const expiryDateStr = await this.orm.call(
                "ir.config_parameter",
                "get_param",
                ["pos_subscription.expiry_date"]
            );

            if (!expiryDateStr || expiryDateStr === "false") {
                return;
            }

            const expiryDate = new Date(expiryDateStr);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            expiryDate.setHours(0, 0, 0, 0);

            const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));

            // Show banner only when 10 days or less are left

//            if (daysLeft <= 10) {
            if (false) {
                this.state.showLicenseBanner = true;
                this.state.licenseBannerTitle = "ðŸ”‘ License Key Status";

                if (daysLeft <= 0) {
                    this.state.licenseBannerMessage =
                        "Your license key has EXPIRED. Please renew immediately.";
                    this.state.licenseBannerType = "danger";
                } else if (daysLeft === 1) {
                    this.state.licenseBannerMessage =
                        "1 DAY LEFT IN EXPIRING LICENSE KEY.";
                    this.state.licenseBannerType = "danger";
                } else {
                    this.state.licenseBannerMessage =
                        `${daysLeft} DAYS LEFT IN EXPIRING LICENSE KEY.`;
                    this.state.licenseBannerType = "warning";
                }
            }
        } catch (error) {
            console.warn("Could not load license and expiry info:", error);
        }
    }

    async _checkSubscriptionStatus() {
        try {
            const subscriptionType = await this.orm.call(
                "ir.config_parameter", "get_param",
                ["pos_subscription.subscription_type"]
            ) || "trial";

            let startDateStr, days;
            if (subscriptionType === "trial") {
                startDateStr = await this.orm.call(
                    "ir.config_parameter", "get_param",
                    ["pos_subscription.trial_start_date"]
                );
                days = parseInt(await this.orm.call(
                    "ir.config_parameter", "get_param",
                    ["pos_subscription.trial_days"]
                ) || 0);
            } else {
                startDateStr = await this.orm.call(
                    "ir.config_parameter", "get_param",
                    ["pos_subscription.license_start_date"]
                );
                days = parseInt(await this.orm.call(
                    "ir.config_parameter", "get_param",
                    ["pos_subscription.license_days"]
                ) || 0);
            }

            if (!startDateStr || isNaN(days)) {
                this._blockUI(subscriptionType);
                return;
            }

            const startDate = new Date(startDateStr);
            const expiryDate = new Date(startDate);
            expiryDate.setDate(expiryDate.getDate() + days);

            const today = new Date();
            today.setHours(0,0,0,0);
            expiryDate.setHours(0,0,0,0);

            if (today > expiryDate) {
                // Subscription expired
                this._blockUI(subscriptionType);
            }
        } catch (error) {
            console.warn("Subscription check failed:", error);
            this._blockUI("unknown");
        }
    }

    _blockUI(type) {
        // Full-screen forbidden overlay
        if (document.getElementById("subscription-expired-overlay")) return;

        const overlay = document.createElement("div");
        overlay.id = "subscription-expired-overlay";
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.backgroundColor = "rgba(0,0,0,0.85)";
        overlay.style.color = "#fff";
        overlay.style.display = "flex";
        overlay.style.alignItems = "center";
        overlay.style.justifyContent = "center";
        overlay.style.zIndex = "9999";
        overlay.style.fontSize = "24px";
        overlay.style.fontWeight = "bold";
        overlay.style.textAlign = "center";
        overlay.style.pointerEvents = "all";
        overlay.innerText = `${type} expired. Access forbidden. Please contact administrator.`;

        document.body.appendChild(overlay);
    }

    /**
     * Close the trial or license banner
     * @private
     */
    _closeBanner(bannerType) {
        if (bannerType === "trial") {
            this.state.showTrialBanner = false;
        } else if (bannerType === "license") {
            this.state.showLicenseBanner = false;
        }
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @param {Object} params
     * @param {HTMLElement} params.element
     * @param {HTMLElement} params.previous
     */
    _sortAppDrop({ element, previous }) {
        const order = this.props.apps.map((app) => app.xmlid);
        const elementId = element.children[0].dataset.menuXmlid;
        const elementIndex = order.indexOf(elementId);
        // first remove dragged element
        order.splice(elementIndex, 1);
        if (previous) {
            const prevIndex = order.indexOf(previous.children[0].dataset.menuXmlid);
            // insert dragged element after previous element
            order.splice(prevIndex + 1, 0, elementId);
        } else {
            // insert dragged element at beginning if no previous element
            order.splice(0, 0, elementId);
        }
        // apply new order
        this.props.reorderApps(order);
        user.setUserSettings("homemenu_config", JSON.stringify(order));
    }

    /**
     * @param {Object} params
     * @param {HTMLElement} params.element
     */
    _sortStart({ element, addClass }) {
        addClass(element.children[0], "o_dragged_app");
    }

    /**
     * @private
     * @param {Object} app
     */
    _onAppClick(app) {
        this._openMenu(app);
    }

    /**
     * @private
     */
    _registerHotkeys() {
        const hotkeys = [
            ["ArrowDown", () => this._updateFocusedIndex("nextLine")],
            ["ArrowRight", () => this._updateFocusedIndex("nextColumn")],
            ["ArrowUp", () => this._updateFocusedIndex("previousLine")],
            ["ArrowLeft", () => this._updateFocusedIndex("previousColumn")],
            ["Tab", () => this._updateFocusedIndex("nextElem")],
            ["shift+Tab", () => this._updateFocusedIndex("previousElem")],
            [
                "Enter",
                () => {
                    const menu = this.displayedApps[this.state.focusedIndex];
                    if (menu) {
                        this._openMenu(menu);
                    }
                },
            ],
            ["Escape", () => this.homeMenuService.toggle(false)],
        ];
        hotkeys.forEach((hotkey) => {
            useHotkey(...hotkey, {
                allowRepeat: true,
            });
        });
        useExternalListener(window, "keydown", this._onKeydownFocusInput);
    }

    _onKeydownFocusInput() {
        if (
            document.activeElement !== this.inputRef.el &&
            this.ui.activeElement === document &&
            !["TEXTAREA", "INPUT"].includes(document.activeElement.tagName)
        ) {
            this._focusInput();
        }
    }

    _onInputSearch() {
        const onClose = () => {
            this._focusInput();
            if (this.inputRef.el) {
                this.inputRef.el.value = "";
            }
        };
        const searchValue = this.compositionStart ? "/" : `/${this.inputRef.el.value.trim()}`;
        this.compositionStart = false;
        this.command.openMainPalette({ searchValue, FooterComponent }, onClose);
    }

    _onInputBlur() {
        if (hasTouch()) {
            return;
        }
        // if we blur search input to focus on body (eg. click on any
        // non-interactive element) restore focus to avoid IME input issue
        setTimeout(() => {
            if (document.activeElement === document.body && this.ui.activeElement === document) {
                this._focusInput();
            }
        }, 0);
    }

    _onCompositionStart() {
        this.compositionStart = true;
    }
}
