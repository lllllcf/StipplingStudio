#pragma once

#include "graphics/shape.h"
#include "Eigen/StdList"
#include "Eigen/StdVector"
#include "Eigen/Sparse"

#include <set>

#if defined(_WIN32) || defined(_WIN64)
#include <omp.h>

// Check for Mac OS
#elif defined(__APPLE__) && defined(__MACH__)
#include "/opt/homebrew/Cellar/libomp/18.1.3/include/omp.h"

// Check for Linux
#elif defined(__linux__)
#include <omp.h>

#else
#error "Unknown operating system"
#endif

#include "mainwindow.h"

#include <QImage>
#include <QVector>
#include <QScreen>
//#include <QMainWindow>

#include "jc_voronoi.h"
#include "draw.h"

// #include <QOffscreenSurface>
// #include <QOpenGLContext>
// #include <QOpenGLFramebufferObject>
// #include <QOpenGLShaderProgram>
// #include <QOpenGLVertexArrayObject>

struct CellEdge
{
    std::vector<std::pair<Eigen::Vector2f, Eigen::Vector2f> > edges;
};

struct Stipple
{
    Eigen::Vector2f pos;
    float size;
    QColor color;

    // animarion
    bool moving;
    Eigen::Vector2f aim_pos;
    float speed;
    float aim_size;
    CellEdge edges;
    bool is_delete;
};

struct Cell
{
    Eigen::Vector2f centroid;
    float orientation;
    float area;
    float total_density;
};



class IndexMap;

class WLBG
{
public:
    QImage m_image;
    QImage m_density;
    QSize m_size;

public:
    WLBG();
    std::vector<Stipple> stippling(Canvas *m_canvas, WLBG *wlbg, bool isVoronoi);
    void paint(Canvas *m_canvas, std::vector<Stipple> points, int iteration);

    // stipples
    std::vector<Stipple> init_stipples();
    float current_stipple_size(Cell cell);

    // voronoi
    std::vector<Cell> generate_voronoi_cells(std::vector<Stipple> points, draw &d, std::vector<CellEdge> &cellEdges, std::vector<int> &index);
    void split_cell(std::vector<Stipple>& stipples, Cell cell, float point_size);
    std::vector<Cell> accumulateCells(const IndexMap& map);

    // utils
    int find_nearest_point(const std::vector<Stipple>& points, float pos_x, float pos_y);
    float calculate_lower_density_bound(float point_size, float hysteresis);
    float calculate_upper_density_bound(float point_size, float hysteresis);
    Eigen::Vector2f jitter(Eigen::Vector2f s);
    int min2(int a, int b);
    int max2(int a, int b);
    int min3(int a, int b, int c);
    int max3(int a, int b, int c);
    bool isInsideTriangle(jcv_point a, jcv_point b, jcv_point c, jcv_point p);

    //ani
    void paint_point_voronoi(Canvas *m_canvas, std::vector<Stipple> points, int iteration, std::vector<CellEdge> cellEdges);
};

// Index Map
class IndexMap {
public:
    int32_t width;
    int32_t height;

    IndexMap(int32_t w, int32_t h, int32_t count);
    void set(const int32_t x, const int32_t y, const uint32_t value);
    uint32_t get(int32_t x, const int32_t y) const;
    int32_t count() const;

private:
    int32_t m_numEncoded;
    QVector<uint32_t> m_data;
};

// Moment
struct Moments {
    float moment00;
    float moment10;
    float moment01;
    float moment11;
    float moment20;
    float moment02;
};
