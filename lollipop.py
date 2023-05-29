from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import mark_inset, zoomed_inset_axes
from matplotlib.ticker import FormatStrFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np


def apply_alpha(arr_img, alpha=1.0):
    """Helper method to apply an alpha to a numpy array image"""
    new_arr_img = np.zeros(
        shape=(arr_img.shape[0], arr_img.shape[1], 4), dtype=arr_img.dtype
    )
    for i, m in enumerate(arr_img):
        for j, n in enumerate(m):
            new_arr_img[i][j] = np.append(arr_img[i][j], alpha)
    return new_arr_img


def plot_lollipop(
    ordered_df,
    figsize=(10, 10),
    log=True,
    hlines=False,
    zoom_factor=3,
    num_in_zoom=3,
    indices=None,
    labels=None,
    bold_labels=None,
):
    alpha = 1
    my_range = range(0, len(ordered_df.index))

    neuro_max_lim = ordered_df["count_neuro"].max()
    cn_max_lim = ordered_df["count_cn"].max()
    if not log:
        neuro_max_lim += 100
        cn_max_lim += 10
    factor = neuro_max_lim / cn_max_lim

    # Change color if in Africa
    my_size = np.where(ordered_df["region"] == "Africa", 40, 40)
    my_color = np.where(ordered_df["region"] == "Africa", "orange", "skyblue")
    indx_africa = np.where(my_color == "orange")[0][0]
    indx_row = np.where(my_color == "skyblue")[0][0]
    africa = ordered_df[ordered_df["region"] == "Africa"]["count_neuro"].head(1)
    row = ordered_df[ordered_df["region"] != "Africa"]["count_neuro"].head(1)

    fig, ax = plt.subplots(1, 1, figsize=figsize, sharey=True)

    # create zooms
    if indices is None:
        indices = [0, "South Africa", -1]
    locs = ["upper center", "center right", "lower right"]
    axins = []
    for i in range(len(indices)):
        if i < len(locs):
            loc = locs[i]
        else:
            loc = "best"
        axin: plt.Axes = zoomed_inset_axes(ax, zoom_factor, loc=loc)
        axin.set_facecolor("w")
        axins.append(axin)

    if log:
        for i, ax_i in enumerate([ax] + axins):
            ax_i.set_xscale("log")

    # do some formatting of the axis before possible duplication with twiny()
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.grid(axis="x", which="major")

    cols = {"count_cn": "Computational Neuroscience", "count_neuro": "Neuroscience"}

    # plot specific points for legend
    ax.scatter(
        [],
        [],
        color="skyblue",
        s=my_size[0] * 4,
        alpha=alpha,
        marker="o",
        label="Computational Neuroscience",
    )
    ax.scatter(
        [],
        [],
        color="skyblue",
        s=my_size[0] * 4,
        alpha=alpha,
        marker="x",
        label="Neuroscience",
    )
    ax.scatter(
        [],
        [],
        color="orange",
        s=my_size[0] * 4,
        alpha=alpha,
        marker="o",
        label="Africa",
    )
    ax.scatter(
        [],
        [],
        color="skyblue",
        s=my_size[0] * 4,
        alpha=alpha,
        marker="o",
        label="Rest of World",
    )

    # because of the zooms, points are plotted multiple times (otherwise 'zoom' views would be empty)
    for i, ax_i in enumerate([ax] + axins):
        # plot computational neuroscience points
        ax_i.scatter(
            ordered_df["count_cn"],
            my_range,
            color=my_color,
            marker="o",
            s=my_size * (4 if i > 0 else 1),
            alpha=alpha,
            label=None,
        )

    if not log:
        # create a second axis for the other count
        # set formatting options before 'twiny'

        ax.set_xlim([0, cn_max_lim])
        ax.legend(loc="left")
        ax.grid(axis="x")
        ax.set_xlabel(f"Number of Computational Neuroscience Publications")
        ax.autoscale(True)

        ax = ax.twiny()
        # use original frame
        ax.set_frame_on(False)

    for i, ax_i in enumerate([ax] + axins):
        # plot neuroscience points
        ax_i.scatter(
            ordered_df["count_neuro"],
            my_range,
            color=my_color,
            marker="x",
            s=my_size * (4 if i > 0 else 1),
            alpha=alpha,
            label=None,
        )

    #     ax.set_xlim([0,neuro_max_lim])

    if hlines:
        # draw connections between "computational neuroscience" and "neuroscience" publications counts
        if log:
            xmin = ordered_df["count_cn"]
        else:
            xmin = ordered_df["count_cn"] * factor
        xmax = ordered_df["count_neuro"]
        for ax_i in [ax] + axins:
            ax_i.hlines(y=my_range, xmin=xmin, xmax=xmax, color="grey", alpha=0.3)

    ax.get_xaxis().set_label_position("bottom")
    ax.get_xaxis().set_ticks_position("bottom")
    if log:
        # change scale to 1,10,100,etc. instead of 10^0,10^1,10^2,etc.
        ax.get_xaxis().set_major_formatter(FormatStrFormatter("%.0f"))
        ax.set_xlabel("Number of Publications")
        ax.spines["left"].set_color("none")
        ax.get_yaxis().set_visible(False)
    else:
        # adjust 2nd xaxis a little
        ax.spines["bottom"].set_position(("axes", -0.01 * figsize[1]))
        # Add title and axes names
        ax.set_xlabel("# Neuroscience Publications")
        ax.set_yticks(my_range)
        ax.set_yticklabels(ordered_df["name"] + " (" + ordered_df.index + ")")
        ax.set_ylabel("Country Code")
        ax.get_yaxis().set_visible(True)

    leg = ax.legend(
        bbox_to_anchor=(0.0, 1.0, 1.0, 0.05),
        loc="upper center",
        ncol=4,
        mode="expand",
        borderaxespad=0.0,
        frameon=False,
        fontsize="large",
    )
    for legend_text in leg.get_texts():
        if legend_text.get_text() == "Rest of World":
            plt.setp(legend_text, alpha=0.35)
    ax.set_ylim([0, my_range[-1] + 1])
    ax.set_xlim(0.4)  # apply the x-limits

    # zooms
    x_min = "count_cn"
    x_max = ["count_cn", "count_neuro"][0]
    for i, axin in zip(indices, axins):
        if i == 0:
            top_x = ordered_df.iloc[-num_in_zoom:]
            top_y = my_range[-num_in_zoom:]
        elif i == -1:
            top_x = ordered_df.iloc[:num_in_zoom]
            top_y = my_range[:num_in_zoom]
        else:
            if type(i) is str:
                i = np.where(ordered_df["name"] == i)[0][0]
            adjust = int((num_in_zoom - 1) / 2)
            top_x = ordered_df.iloc[i - adjust : i + 1 + adjust]
            top_y = my_range[i - adjust : i + 1 + adjust]
        x1, x2, y1, y2 = (
            np.min(top_x[x_min]),
            np.max(top_x[x_max]),
            np.min(top_y),
            np.max(top_y),
        )
        #     3.7, 4.6 # specify the limits
        axin.set_xlim(x1 - x1 / 10, x2 + x2 / 4)  # apply the x-limits
        axin.set_ylim(y1 - 1, y2 + 1)  # apply the y-limits

        axin.set_xticks([])
        axin.get_xaxis().set_visible(False)
        axin.set_yticks(top_y)
        y_labels = []
        for name, number in zip(top_x["name"], top_y):
            y_labels.append(f"{name}")
        axin.set_yticklabels(y_labels)

        for label, x, y, indx in zip(
            ordered_df[ordered_df.index.isin(top_x.index)][x_min],
            top_x[x_min].values,
            top_y,
            top_x.index.values,
        ):
            indx = indx.lower()
            if indx == "usa":
                indx = "us"
            try:
                arr_img = plt.imread(
                    f"famfamfam_flag_icons/png/{indx}.png", format="png"
                )
            except BaseException:
                print(indx)
                continue
            axin.annotate(
                label,
                xy=(x, y),
                xytext=(10, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                bbox=dict(boxstyle="square,pad=0.1", fc="w", ec="w", alpha=1),
                #         arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
            )

            imagebox = OffsetImage(arr_img, zoom=1)
            imagebox.image.axes = ax
            ab = AnnotationBbox(
                imagebox,
                (x, y),
                xybox=(x, y),
                xycoords="data",
                boxcoords="data",
                pad=0.0,
            )

            axin.add_artist(ab)

        if x_min != x_max:
            for label, x, y in zip(
                ordered_df[ordered_df.index.isin(top_x.index)][x_max],
                top_x[x_max].values,
                top_y,
            ):
                axin.annotate(
                    label,
                    xy=(x, y),
                    xytext=(-10, 6),
                    textcoords="offset points",
                    ha="right",
                    va="center",
                    bbox=dict(
                        boxstyle="square,pad=0.1", fc="skyblue", ec="w", alpha=0.5
                    ),
                    #         arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0')
                )

        # link zooms to main axis
        mark_inset(ax, axin, loc1=2, loc2=3, fc="none", ec="0.5")

    # add flags
    if bold_labels is None:
        bold_labels = []
    if labels is not None:
        y_max = my_range[-1] + 1
        for label in labels:
            if type(label) is str:
                i = np.where(ordered_df["name"] == label)[0][0]
            else:
                i = label
                label = ordered_df.iloc[i]["name"]
            x = ordered_df.iloc[i]["count_cn"]
            y = my_range[i]
            xy = (x - x / 20, y)
            xy_offset = (0.4, y)  # in data coords

            format_option = [f"{label} {x:>10g}", f"{x:g}"][1]

            alpha = 1
            if i not in bold_labels:
                # 35% opacity
                alpha = 0.35

            # add flag
            indx = ordered_df.iloc[i].name.lower()
            if indx == "usa":
                indx = "us"
            try:
                arr_img = plt.imread(
                    f"famfamfam_flag_icons/png/{indx}.png", format="png"
                )
                arr_img = apply_alpha(arr_img, alpha)
            except BaseException:
                print(f"flag not found: {indx} - {label}")
                continue
            else:
                ax.annotate(
                    label,
                    xy=xy_offset,
                    xytext=(-15, 0),
                    textcoords="offset points",
                    ha="right",
                    va="center",
                    fontsize="x-large",
                    alpha=alpha,
                    bbox=dict(boxstyle="round,pad=0.2", fc="skyblue", alpha=0),
                )

                imagebox = OffsetImage(arr_img, zoom=1)
                imagebox.image.axes = ax
                xy = xy
                ab = AnnotationBbox(
                    imagebox,
                    xy,
                    xybox=xy_offset,
                    xycoords="data",
                    pad=0.0,
                    bboxprops=dict(facecolor="none", edgecolor="none"),
                    arrowprops=dict(
                        arrowstyle="-", connectionstyle="arc3,rad=-0", alpha=0.09
                    ),
                )
                ax.add_artist(ab)
                color = "skyblue" if i not in bold_labels else "orange"
                ax.annotate(
                    format_option,
                    xy=xy_offset,
                    xytext=(50, 0),
                    textcoords="offset points",
                    ha="right",
                    va="center",
                    fontsize="medium",
                    alpha=alpha,
                    bbox=dict(boxstyle="round,pad=0.1", ec=color, fc="w", alpha=1),
                )
